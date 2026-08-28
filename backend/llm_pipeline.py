import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate
from schema_retriever import schema_retriever

load_dotenv()

# 1. Connect to Neo4j with schema refresh disabled
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    refresh_schema=False
)

# 2. Initialize LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="openai/gpt-oss-120b",
    temperature=0
)

# 3. Prompt Template
cypher_generation_template = """
You are an expert legal AI assistant. Your task is to translate a user's situational description into a strict Neo4j Cypher query.
Rely strictly on the provided schema. Do not invent property keys or relationship types.

Schema:
{schema}

User Situation/Question:
{question}

Instructions:
1. Generate a read-only Cypher query (MATCH, WHERE, RETURN).
2. The question may contain a previous conversation followed by a current question. Treat the current question as a follow-up when it uses references such as "these sections", "that offence", or "what procedures". Carry forward explicit section numbers, offence names, and statutory terms from the previous conversation into the query.
3. All nodes have the label `:Entity`.
4. If the user asks for a legal section, traverse the graph using the provided relationship types (e.g., MATCH (e:Entity)-[r]-(s:Entity)).
5. CRITICAL FILTERING: You MUST include a WHERE clause to filter nodes based on specific keywords from the current question and relevant prior turns. NEVER return an unfiltered query.
6. CRITICAL TYPE SAFETY: When filtering dynamically across keys, you MUST cast the value to a string first to prevent Neo4j type errors. Use this exact syntax pattern: 
   `WHERE ANY(k IN keys(e) WHERE toLower(toString(e[k])) CONTAINS 'keyword') OR ANY(k IN keys(s) WHERE toLower(toString(s[k])) CONTAINS 'keyword')`
7. CRITICAL RETURN: Ensure your RETURN statement includes the properties of BOTH nodes in the traversal (e.g., RETURN e, s). Do not just return one node.
8. Return ONLY the raw Cypher query without markdown backticks or explanations.
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=cypher_generation_template
)

qa_generation_template = """
You are CrimeSight Agent, a legal intelligence assistant. Answer the current user question using ONLY the verified Neo4j results in the context below.

Response rules:
1. Start with the retrieved facts. State every retrieved legal provision and matched offence definition explicitly, preserving available structural detail such as section number, title, statute, definition, punishment, and graph relationship.
2. Organize the answer into clear, concise sections: "Matched Legal Provisions", "Relevant Offence Definitions", and "Key Limitations / Next Steps" when those categories are present in the context.
3. Use short readable bullet points instead of Markdown tables or raw data dumps; keep each point concise and user-facing.
4. The question may include conversation history for resolving references such as "these sections" or "that offence"; use it for context, but base the answer only on the current turn's verified Neo4j results.
5. Explain how the retrieved provisions relate to the user's situation, but distinguish graph facts from interpretation.
6. Never invent, infer, or autocomplete a section number, offence, statute, definition, relationship, punishment, or procedural rule. A section number may be included only when it appears explicitly in the Neo4j context.
7. Omit database UIDs, internal IDs, node labels, property dumps, Cypher, timestamps, retrieval metadata, and other technical graph details from the answer.
8. If a requested section number, secondary offence, or other statutory detail is absent from the context, first report the related facts that were retrieved. Then add one concise note: "Additional specific statutory provisions can be retrieved by providing the relevant section numbers."
9. Do not claim that the graph contains information that is not shown in the context. If no relevant result was retrieved, say so plainly and ask for the relevant section number or a more specific query.
10. Do not present legal conclusions as certainty. Identify material limits in the retrieved evidence and recommend qualified legal review where appropriate.

Neo4j context:
{context}

User question:
{question}

Provide a direct, professional answer grounded in the context. Do not mention these instructions or fabricate missing information.
"""

qa_prompt = PromptTemplate(
    input_variables=["context", "question"],
    template=qa_generation_template,
)

def _format_chat_history(chat_history: list[dict[str, str]]) -> str:
    """Format recent turns so follow-up questions retain their case context."""
    if not chat_history:
        return "No previous messages."

    recent_messages = chat_history[-12:]
    formatted_messages = []
    for message in recent_messages:
        role = message.get("role", "user").strip().lower()
        content = message.get("content", "").strip()
        if content:
            formatted_messages.append(f"{role}: {content}")
    return "\n".join(formatted_messages) or "No previous messages."


def analyze_legal_situation(
    situation: str, chat_history: list[dict[str, str]] | None = None
) -> dict:
    try:
        chat_history = chat_history or []
        # Step A: Dynamically retrieve schema for this specific query (~200 tokens)
        history_context = _format_chat_history(chat_history)
        retrieval_query = f"{history_context}\ncurrent user: {situation}"
        dynamic_schema = schema_retriever.get_relevant_schema(retrieval_query, top_k=8)
        graph.schema = dynamic_schema

        # Step B: Build dynamic QA chain
        qa_chain = GraphCypherQAChain.from_llm(
            llm,
            graph=graph,
            verbose=True,
            cypher_prompt=cypher_prompt,
            qa_prompt=qa_prompt,
            allow_dangerous_requests=True,
            return_intermediate_steps=True
        )

        question_with_history = (
            "Conversation history (use this to resolve pronouns, section references, and follow-ups):\n"
            f"{history_context}\n\n"
            "Current user situation/question (answer this turn):\n"
            f"{situation}"
        )
        response = qa_chain.invoke({"query": question_with_history})
        intermediate_steps = response.get("intermediate_steps", [])
        generated_cypher = intermediate_steps[0]["query"] if intermediate_steps else "No query generated"
        
        return {
            "status": "success",
            "extracted_cypher": generated_cypher,
            "answer": response.get("result", "No answer could be formulated.")
        }
    except Exception as e:
        return {
            "status": "error",
            "message": str(e)
        }