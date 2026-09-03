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
- **Conversational Memory:** Preserves recent user and agent turns so follow-up questions can resolve context and pronouns.
- **Interactive React Frontend:** Provides a responsive landing page and agent workspace with animated processing states, case titles, chat history, and graph evidence.
- **High-Performance FastAPI Backend:** Provides a REST API for frontend integration and client consumption.

## Architecture

```text
User Situational Query
	|
	v
+----------------------------------+
| FastAPI API and Agent Interface  |
+----------------+-----------------+
		 |
		 v
+----------------------------------+
| Current GraphRAG Pipeline        |
|                                  |
|  1. Schema Semantic Retriever    |
|     TF-IDF over 2,300+ patterns  |
|  2. Groq LLM Text-to-Cypher      |
|  3. Neo4j BNS Knowledge Graph    |
|  4. Grounded Legal Synthesis     |
+----------------+-----------------+
		 |
		 v
	Verified Legal Answer
		 |
		 v
	React Agent Workspace

Planned Agent Orchestration Layer
	|
	+--> Automated FIR and Legal Petition Draft Generator
	|       Extract incident details such as dates, amounts, scammer
	|       handles, and locations; structure FIR or bank-freezing
	|       complaints; cite relevant BNS and BNSS provisions.
	|
	+--> Cross-Jurisdiction and Procedural Guidance Agent
	|       Analyze geographic constraints and explain procedural rules,
	|       service mechanisms, warrants, and compulsory attendance steps.
	|
	+--> Evidence-to-Statute Compliance Matcher
		Compare uploaded evidence or text logs with the Neo4j graph,
		identify matched provisions and statutory gaps, and produce
		an admissible-evidence checklist for filing or hearings.
```

The current GraphRAG pipeline is implemented today. The agent orchestration
layer is planned for a future phase and will reuse the existing schema
retrieval, Groq, and Neo4j components. Each future agent will return grounded
legal evidence, cite the applicable BNS or BNSS provisions, and clearly
separate retrieved facts from procedural guidance or generated drafts.

## Project Structure

```text
legal-agent/
├── backend/
│   ├── database.py             # Neo4j driver connection and query utilities
│   ├── extract_schema.py       # One-time schema relationship catalog extraction
│   ├── llm_pipeline.py         # Dynamic Cypher generation and conversational GraphQA
│   ├── main.py                 # FastAPI application and endpoint routing
│   ├── schema_catalog.json     # Indexed schema relationship patterns
│   ├── schema_retriever.py     # In-memory TF-IDF Schema RAG retriever
│   └── requirements.txt        # Backend dependencies
└── frontend/
    ├── src/App.jsx             # Landing page, chat workspace, and application state
    ├── src/App.css             # Responsive legal-tech visual system
    ├── src/index.css           # Global styles and fonts
    ├── package.json             # Frontend scripts and dependencies
    └── vite.config.js           # Vite configuration
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

### 7. Install and Run the Frontend

Open a second terminal from the repository root:

```bash
cd frontend
npm install
npm run dev
```

The Vite development server will print the frontend URL, usually `http://localhost:5173`.

### 8. Run the Backend Application

From the `backend/` directory:

```bash
uvicorn main:app --reload
```

The API is available at `http://127.0.0.1:8000`. Interactive documentation is available at `http://127.0.0.1:8000/docs`.

## Frontend Experience

The frontend is built with React, Vite, Tailwind CSS, Framer Motion, and `lucide-react`.

- **Presentation view:** Explains the CrimeSight pipeline through the knowledge graph visualization, architecture flow, and capability sections.
- **Agent workspace:** Provides a collapsible sidebar, empty initial case history, starter prompts, auto-growing incident composer, and responsive chat canvas.
- **Dynamic case history:** The first message in each workspace session creates a short four-word case title. Titles are rendered from React state rather than hardcoded data.
- **Agent trace:** Displays the four processing stages while a request is being analyzed.
- **Evidence view:** Allows users to expand the generated read-only Cypher query and Neo4j execution metadata.
- **Resilient demo flow:** Displays a representative response when the backend is unavailable, making the frontend usable during demonstrations.

### Frontend Commands

```bash
cd frontend
npm run dev       # Start the development server
npm run build     # Create a production build
npm run lint      # Run Oxlint
```

## Example API Usage

### Endpoint

`POST /api/analyze-situation`

### Request

```json
{
	"situation": "A person physically assaulted me on the street causing grievous bodily injuries. Which legal sections cover this assault?",
	"chat_history": []
}
```

### Response

```json
{
	"status": "success",
	"cypher_query": "MATCH (e:Entity)-[r]-(s:Entity)\\nWHERE ANY(k IN keys(e) WHERE toString(e[k]) =~ '(?i).*assault.*')\\n   OR ANY(k IN keys(s) WHERE toString(s[k]) =~ '(?i).*assault.*')\\nRETURN e, s",
	"agent_response": "Section 133 - Assault or criminal force with intent to dishonour person, otherwise than on grave provocation.\nSection 134 - Assault or criminal force in attempt to commit theft of property carried by a person."
}
```


### Conversational Follow-up

The frontend sends previous turns in the next request so the backend can resolve questions such as “What section does that come under?”:

```json
{
  "situation": "What section does that come under?",
  "chat_history": [
    {
      "role": "user",
      "content": "A person physically assaulted me and caused grievous bodily injuries."
    },
    {
      "role": "agent",
      "content": "The graph identified provisions relating to assault causing grievous hurt."
    }
  ]
}
```

The backend formats the most recent 12 turns, combines them with the current question for schema retrieval, and injects them into the Cypher-generation input. The request-based approach keeps sessions isolated and avoids shared server memory between users.

## Challenges and Solutions

### 1. Graph Schema Context Overload

- **Challenge:** Passing the complete Neo4j schema to the LLM created a large prompt and risked Groq token-limit failures.
- **Solution:** Disabled automatic schema refresh and added TF-IDF retrieval to select only the relevant schema patterns for each incident.

### 2. Hallucinated Cypher Properties and Relationships

- **Challenge:** The model could invent property names or relationship directions, producing empty graph results.
- **Solution:** Added strict read-only Cypher instructions, required a filtered `WHERE` clause, constrained nodes to the `Entity` label, and supplied the retrieved schema as the source of truth.

### 3. Stateless Follow-up Questions

- **Challenge:** A new `GraphCypherQAChain` invocation had no knowledge of previous turns, so pronouns and follow-up questions lost their case context.
- **Solution:** Added an optional `chat_history` field to the FastAPI request model. Recent turns are formatted and passed into schema retrieval and Cypher generation.

### 4. Empty or Hardcoded Frontend Case History

- **Challenge:** Static sidebar cases did not represent the user’s current session and made new sessions appear populated.
- **Solution:** Replaced the static list with `sidebarChats` React state. The first submitted message generates a short title and adds it to the sidebar.

### 5. Long-running Agent Feedback

- **Challenge:** Graph and LLM requests can take long enough for users to wonder whether the application is responding.
- **Solution:** Added an animated four-step agent trace covering narrative analysis, schema retrieval, graph traversal, and legal synthesis.

### 6. Backend Availability During Demos

- **Challenge:** The frontend should remain demonstrable when Neo4j, Groq, or FastAPI is temporarily unavailable.
- **Solution:** Added a visible API notice and a representative grounded response fallback while preserving the live API path for connected environments.

## Roadmap

- [x] Neo4j AuraDB knowledge graph connection
- [x] Text-to-Cypher generation via Groq API
- [x] Dynamic Schema Retrieval (Schema RAG)
- [x] React + Tailwind CSS interactive chat interface
- [x] Animated agent trace and expandable Cypher evidence
- [x] Request-based conversational memory for follow-up questions
- [ ] LangGraph multi-agent orchestration for FIR auto-drafting and bail calculation
- [ ] User role authentication and saved case history

## License

This project is licensed under the MIT License.
