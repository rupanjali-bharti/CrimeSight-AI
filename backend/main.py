from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from database import db
from llm_pipeline import analyze_legal_situation # IMPORT YOUR PIPELINE

app = FastAPI(title="Criminal Law Assistant API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SituationRequest(BaseModel):
    situation: str
    chat_history: list[dict[str, str]] = Field(default_factory=list)

@app.get("/")
def root():
    return {"message": "Criminal Law Assistant API is running"}

@app.post("/api/analyze-situation")
def analyze_situation(payload: SituationRequest):
    user_situation = payload.situation.strip()
    if not user_situation:
        raise HTTPException(status_code=400, detail="Situation text cannot be empty.")
    
    # Send the situation to the LLM and Graph
    result = analyze_legal_situation(user_situation, payload.chat_history)
    
    if result["status"] == "error":
        raise HTTPException(status_code=500, detail=result["message"])
        
    return {
        "input_situation": user_situation,
        "cypher_query": result["extracted_cypher"],
        "agent_response": result["answer"]
    }