import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_neo4j import Neo4jGraph
from langchain_neo4j import GraphCypherQAChain
from langchain_core.prompts import PromptTemplate

# Load environment variables
load_dotenv()

# 1. Connect to Neo4j and DISABLE automatic schema fetching
# setting refresh_schema=False stops the 36k token crash
graph = Neo4jGraph(
    url=os.getenv("NEO4J_URI"),
    username=os.getenv("NEO4J_USERNAME"),
    password=os.getenv("NEO4J_PASSWORD"),
    refresh_schema=False  
)


# 2. Inject our accurate schema manually based on the database check
graph.schema = """
Node properties:
Entity {name: STRING, type: STRING, section: STRING, reference: STRING, value_limit: STRING}

Relationship properties:
Entity -[:COVERS_OFFENCE]-> Entity
Entity -[:PROTECTS_AGAINST]-> Entity
Entity -[:EXTENDS_RIGHT_APPLIES_TO_OFFENCE]-> Entity
Entity -[:CONTINUES_AGAINST]-> Entity
"""

# 3. Initialize the Groq LLM
llm = ChatGroq(
    groq_api_key=os.getenv("GROQ_API_KEY"),
    model_name="openai/gpt-oss-120b",
    temperature=0
)

# 4. Create a strict Prompt Template
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
3. ONLY return properties that exist in the schema, such as `name`, `type`, `section`, and `reference`. NEVER use properties like `severity` or `penalty`.
4. If asked about a crime like theft, you can simply match the node and return its properties (e.g., `MATCH (n:Entity) WHERE toLower(n.name) CONTAINS 'theft' RETURN n.name, n.section, n.reference, n.type`).
5. Only use relationships listed in the schema if you need to connect two nodes.
6. Return ONLY the raw Cypher query without markdown formatting, quotes, or explanations.
"""


cypher_prompt = PromptTemplate(
    input_variables=["schema", "question"], 
    template=cypher_generation_template
)

# 5. Initialize the QA Chain
qa_chain = GraphCypherQAChain.from_llm(
    llm,
    graph=graph,
    verbose=True,
    cypher_prompt=cypher_prompt,
    allow_dangerous_requests=True,
    return_intermediate_steps=True
)

def analyze_legal_situation(situation: str) -> dict:
    try:
        response = qa_chain.invoke({"query": situation})
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