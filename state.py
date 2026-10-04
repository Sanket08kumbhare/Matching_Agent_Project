from typing import Any, Dict, List
from typing_extensions import TypedDict
from langchain_core.messages import BaseMessage

class Candidate(TypedDict, total=False):
    candidate_id: str
    name: str
    resume_text: str
    source: str
    score: float
    strengths: List[str]
    gaps: List[str]
    reasoning: List[str]
    recommendation: str
    interview_questions: List[str]
    deep_analysis: str
    improvement_suggestions: List[str]

class Requirements(TypedDict, total=False):
    must_have: List[str]
    nice_to_have: List[str]
    min_years: float
    raw_jd: str

class AgentState(TypedDict, total=False):
    messages: List[BaseMessage]
    conversation_history: List[Dict[str, str]]
    jd: str
    job_requirements: Requirements
    candidates: List[Candidate]
    candidate_shortlist: List[Candidate]
    ranking_reasoning: Dict[str, Any]
    report: Dict[str, Any]
    human_feedback: str
    pending_feedback: bool
    screening_round: int
    deep_screened: List[Candidate]
    final_recommendations: List[Candidate]
    user_query: str
    response: str
