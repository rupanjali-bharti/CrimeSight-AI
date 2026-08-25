# ⚖️ Legal AI Agent - Backend Pipeline

## 📌 Project Overview
Successfully completed Phases 1 & 2 of a Legal AI Agent. The system uses a Text-to-Cypher pipeline to translate natural language user scenarios into precise graph database queries. It retrieves relevant legal provisions based on the Bharatiya Nyaya Sanhita (BNS), 2023 and formulates a grounded, factual legal response.

## 🛠️ Tech Stack

- Backend Framework: Python, FastAPI, Uvicorn
- Database: Neo4j AuraDB (Knowledge Graph)
- AI/LLM Orchestration: LangChain (`langchain-neo4j`, `langchain-groq`)
- LLM Provider: Groq API (`openai/gpt-oss-120b`)
- API Testing: Postman

## 🏗️ Architecture

1. Request Handling: A user sends a JSON POST request to the FastAPI endpoint (`/api/analyze-situation`) containing a legal scenario.
2. Prompt Construction: LangChain combines the user's question with a strictly curated database schema "blueprint" and specific instructional prompts.
3. Cypher Generation: The Groq LLM processes the prompt and generates a read-only Cypher query optimized for our specific Neo4j graph structure.
4. Graph Retrieval: The GraphCypherQAChain executes the query against Neo4j, pulling exact BNS nodes (`Entity`) and their properties (`name`, `section`, `reference`, `type`).
5. Grounded Response: The LLM reads the retrieved graph context to answer the user's original question with actual legal facts, returning the final data as a structured JSON response.

## ⚠️ Problems Faced & 💡 Solutions

### Problem 1: Model Deprecation & Access Errors

- Issue: Initial attempts to use `llama3-70b-8192` and `llama-3.3-70b-versatile` failed due to the models being decommissioned or restricted on the current API tier.
- Solution: Transitioned to the fully supported and highly capable `openai/gpt-oss-120b` model.

### Problem 2: Token Limit Crashes (Context Overload)

- Issue: LangChain's default behavior pulled all 400+ relationship types from the Neo4j database into the prompt. This created a massive 36,000+ token payload, crashing Groq's 8,000 Tokens-Per-Minute (TPM) limit.
- Solution: Bypassed LangChain's automatic scan by instantiating the graph with `refresh_schema=False`. We then manually injected a tiny, curated schema (under 200 tokens) directly into the prompt, completely avoiding the rate limit.

### Problem 3: LLM Hallucinations & Empty Contexts

- Issue: The AI hallucinated properties (e.g., `severity`, `penalty`) and assumed incorrect relationship directions (e.g., `HAS_PUNISHMENT`), causing Neo4j to return empty results (`[]`).
- Solution: We wrote a Python script to ping the database and discover the actual structure for "theft". We updated the schema blueprint and strict prompt instructions to force the LLM to use only valid properties (`section`, `reference`) and real relationships (`COVERS_OFFENCE`, `PROTECTS_AGAINST`).

## ✅ Current Status

The backend pipeline is operational and successfully demonstrates the end-to-end flow from natural language input to grounded legal answers using Neo4j knowledge graph retrieval.

## 📁 Project Structure

```bash
backend/
├── database.py
├── llm_pipeline.py
├── main.py
├── requirements.txt
```
