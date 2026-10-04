# Architecture

## Required LangGraph flow

`START -> Parse JD -> Extract Requirements -> Search Resumes -> Rank Candidates -> Generate Report -> Human Feedback Loop -> END`

## State

`AgentState` stores:
- conversation history
- job description and structured requirements
- all candidates and top-10 shortlist
- ranking reasoning
- report
- human feedback
- screening round
- deep-screened candidates
- final recommendations

## Ranking

Transparent baseline:
- 70% must-have coverage
- 20% nice-to-have coverage
- 10% experience match

## Multi-round screening

1. Initial screen: search all resumes and retain top 10.
2. Second round: deep analysis and targeted interview questions.
3. Final round: Hire / Borderline / No Hire recommendation.

## Explainability

Every ranked candidate contains score, strengths, gaps and reasoning. Borderline candidates receive improvement suggestions.

## Integration points

- Milestone 1: `tools/resume_search.py`
- Milestone 2 RAG: `adapters/rag_adapter.py`
