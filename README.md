# CrimeSight-AI

> An autonomous GraphRAG AI agent for Indian Criminal Law (Bharatiya Nyaya Sanhita, 2023) powered by Neo4j Knowledge Graphs, FastAPI, and Groq.

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue.svg)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-009688.svg)](https://fastapi.tiangolo.com/)
[![Neo4j](https://img.shields.io/badge/Neo4j-AuraDB%20%2F%20Graph-008CC1.svg)](https://neo4j.com/)
[![LangChain](https://img.shields.io/badge/LangChain-Enabled-1C3C3C.svg)](https://www.langchain.com/)
[![Groq](https://img.shields.io/badge/Groq-Llama%203%20%2F%20GPT--OSS-f55036.svg)](https://groq.com/)

---

## Overview

CrimeSight-AI is a domain-specific legal intelligence copilot designed to analyze real-world incident descriptions and map them accurately to the **Bharatiya Nyaya Sanhita (BNS), 2023**.

Unlike traditional vector-search RAG systems that can lose legal context, CrimeSight-AI uses a **Neo4j knowledge graph** structured with legal relationships. By converting natural language into optimized Cypher queries, the system traverses legal provisions, offenses, punishments, and exceptions deterministically.

## Key Features

- **Dynamic Schema Retrieval (Schema RAG):** Dynamically indexes and retrieves relevant graph relationships from 2,300+ schema patterns using in-memory TF-IDF vectorization.
- **Natural Language to Cypher Translation:** Translates unstructured situation descriptions into precise graph traversal queries.
- **Full Relationship Traversal:** Navigates complex paths connecting offenses, sections, value limits, and legal exceptions such as the Right of Private Defence.
- **Grounded Answers:** Restricts answer formulation to data returned from the verified BNS knowledge graph.
- **High-Performance FastAPI Backend:** Provides an asynchronous REST API for frontend integration and client consumption.

## Architecture

```text
User Situational Query
					|
					v
+----------------------------------+
|     Schema Semantic Retriever    |
|   TF-IDF over 2,300+ Patterns    |
+----------------+-----------------+
								 |
								 v
		Top Relevant Schema Subset
								 |
								 v
+----------------------------------+
|      Groq LLM (Text-to-Cypher)   |
+----------------+-----------------+
								 |
								 v
			 Generated Cypher Query
								 |
								 v
+----------------------------------+
|       Neo4j Knowledge Graph      |
|          BNS 2023 Nodes          |
+----------------+-----------------+
								 |
								 v
			 Extracted Legal Context
								 |
								 v
		Grounded Legal Answer Synthesis
```

## Project Structure

```text
legal-agent/
└── backend/
		├── database.py             # Neo4j driver connection and query utilities
		├── extract_schema.py       # One-time schema relationship catalog extraction
		├── llm_pipeline.py         # Dynamic Cypher generation and GraphQA chain
		├── main.py                 # FastAPI application and endpoint routing
		├── schema_catalog.json      # Indexed schema relationship patterns
		├── schema_retriever.py     # In-memory TF-IDF Schema RAG retriever
		└── requirements.txt         # Backend dependencies
```

## Getting Started

### 1. Prerequisites

- Python 3.10+
- Neo4j AuraDB instance loaded with the BNS 2023 dataset
- Groq Cloud API key

### 2. Clone the Repository

```bash
git clone https://github.com/rupanjali-bharti/CrimSight-AI.git
cd CrimSight-AI/backend
```

### 3. Set Up a Virtual Environment

**Windows:**

```powershell
python -m venv venv
.\venv\Scripts\activate
```

**macOS/Linux:**

```bash
python3 -m venv venv
source venv/bin/activate
```

### 4. Install Dependencies

```bash
pip install -r requirements.txt
```

### 5. Configure Environment Variables

Create a `.env` file in the `backend/` directory:

```env
NEO4J_URI=neo4j+s://<YOUR_INSTANCE_ID>.databases.neo4j.io
NEO4J_USERNAME=neo4j
NEO4J_PASSWORD=<YOUR_NEO4J_PASSWORD>
GROQ_API_KEY=<YOUR_GROQ_API_KEY>
```

Do not commit `.env` or expose these credentials publicly.

### 6. Extract the Schema Catalog

Run this script once to index your database's relationship patterns:

```bash
python extract_schema.py
```

### 7. Run the Application

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Example API Usage

### Endpoint

`POST /api/analyze-situation`

### Request

```json
{
	"situation": "A person physically assaulted me on the street causing grievous bodily injuries. Which legal sections cover this assault?"
}
```

### Response

```json
{
	"status": "success",
	"extracted_cypher": "MATCH (e:Entity)-[r]-(s:Entity)\\nWHERE ANY(k IN keys(e) WHERE toString(e[k]) =~ '(?i).*assault.*')\\n   OR ANY(k IN keys(s) WHERE toString(s[k]) =~ '(?i).*assault.*')\\nRETURN e, s",
	"agent_response": "Section 133 - Assault or criminal force with intent to dishonour person, otherwise than on grave provocation.\nSection 134 - Assault or criminal force in attempt to commit theft of property carried by a person."
}
```

## Roadmap

- [x] Neo4j AuraDB knowledge graph connection
- [x] Text-to-Cypher generation via Groq API
- [x] Dynamic Schema Retrieval (Schema RAG)
- [ ] React + Tailwind CSS interactive chat interface
- [ ] LangGraph multi-agent orchestration for FIR auto-drafting and bail calculation
- [ ] User role authentication and saved case history

## License

This project is licensed under the MIT License.
