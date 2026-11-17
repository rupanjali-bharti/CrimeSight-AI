from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from llm_pipeline import analyze_legal_situation, graph
from evidence_matcher import analyze_case_evidence
from fir_draft import (
    checklist_is_complete,
    compile_fir_draft,
    extract_case_details,
)
from statute_retriever import retrieve_bns_statutes

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
    """Analyze a turn using the frontend-provided conversation history."""
    user_situation = payload.situation.strip()
    if not user_situation:
        raise HTTPException(status_code=400, detail="Situation text cannot be empty.")
    
    case_analysis = analyze_case_evidence(
        user_situation,
        payload.chat_history,
    )

    # Send the full conversation, latest turn, and checklist to the agent.
    result = analyze_legal_situation(
        user_situation,
        payload.chat_history,
        case_analysis,
    )
    
    if result["status"] == "error":
        raise HTTPException(
            status_code=502,
            detail="Legal analysis is temporarily unavailable.",
        )

    return {
        "input_situation": user_situation,
        "cypher_query": result["extracted_cypher"],
        "reply": result["reply"],
        "agent_response": result["reply"],
        "detected_category": case_analysis["category_label"],
        "evidence_checklist": case_analysis["evidence_checklist"],
        "fir_ready": case_analysis["fir_ready"],
        "case_analysis": case_analysis,
        "matched_statutes": result.get("matched_statutes", []),
    }


@app.post("/api/generate-fir-draft")
def generate_fir_draft(payload: SituationRequest):
    """Generate a review-ready draft only after every checklist item is mentioned."""
    user_situation = payload.situation.strip()
    if not user_situation:
        raise HTTPException(status_code=400, detail="Situation text cannot be empty.")

    case_analysis = analyze_case_evidence(user_situation, payload.chat_history)
    checklist = case_analysis["evidence_checklist"]
    if not checklist_is_complete(checklist):
        raise HTTPException(
            status_code=409,
            detail={
                "message": "All evidence checklist items must be mentioned before generating a draft.",
                "detected_category": case_analysis["category_label"],
                "evidence_checklist": checklist,
                "fir_ready": False,
            },
        )

    user_turns = [
        message.get("content", "").strip()
        for message in payload.chat_history
        if message.get("role", "user").strip().lower() == "user"
        and message.get("content", "").strip()
    ]
    if not user_turns or user_turns[-1] != user_situation:
        user_turns.append(user_situation)

    try:
        matched_statutes = retrieve_bns_statutes(
            graph, case_analysis["category"]
        )
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The statute graph is unavailable; the draft was not generated.",
        ) from exc

    case_narrative = "\n\n".join(user_turns)
    case_details = extract_case_details(case_narrative)
    draft = compile_fir_draft(
        case_narrative=case_narrative,
        category_label=case_analysis["category_label"],
        evidence_checklist=checklist,
        matched_statutes=matched_statutes,
        case_details=case_details,
    )
    return {
        "draft": draft,
        "case_details": case_details,
        "detected_category": case_analysis["category_label"],
        "evidence_checklist": checklist,
        "fir_ready": True,
        "matched_statutes": matched_statutes,
    }