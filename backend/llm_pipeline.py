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
2. All nodes have the label `:Entity`.
3. If the user asks for a legal section, traverse the graph using the provided relationship types (e.g., MATCH (e:Entity)-[r]-(s:Entity)).
4. CRITICAL FILTERING: You MUST include a WHERE clause to filter nodes based on specific keywords from the user's situation. NEVER return an unfiltered query.
5. CRITICAL TYPE SAFETY: When filtering dynamically across keys, you MUST cast the value to a string first to prevent Neo4j type errors. Use this exact syntax pattern: 
   `WHERE ANY(k IN keys(e) WHERE toLower(toString(e[k])) CONTAINS 'keyword') OR ANY(k IN keys(s) WHERE toLower(toString(s[k])) CONTAINS 'keyword')`
6. CRITICAL RETURN: Ensure your RETURN statement includes the properties of BOTH nodes in the traversal (e.g., RETURN e, s). Do not just return one node.
7. Return ONLY the raw Cypher query without markdown backticks or explanations.
"""

cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"],
    template=cypher_generation_template
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
            allow_dangerous_requests=True,
            return_intermediate_steps=True
        )

        question_with_history = (
            "Previous conversation (use this to resolve pronouns and follow-ups):\n"
            f"{history_context}\n\n"
            f"Current user situation/question:\n{situation}"
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