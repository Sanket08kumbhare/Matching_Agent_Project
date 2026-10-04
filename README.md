# Matching Agent — LangGraph Resume Matching & Screening

Assignment-ready Python project implementing Parts A, B and C.

## Flow

START → Parse JD → Extract Requirements → Search Resumes → Rank Candidates → Generate Report → Human Feedback Loop → END

## Features

- LangGraph stateful agent
- Conversation history
- Job requirement understanding
- Candidate shortlist and transparent ranking reasoning
- Filesystem resume search
- Milestone-2 RAG adapter
- `extract_requirements(jd)`
- `compare_candidates(candidate_ids)`
- `generate_interview_questions(candidate_id)`
- Natural-language candidate search
- Side-by-side comparison
- Ranking explanation
- Iterative requirement refinement and re-ranking
- Multi-round screening: top 10 → deep screening → final recommendation
- Strengths, gaps and borderline improvement suggestions
- Interactive CLI
- Unit tests and sample data

## Setup

Python 3.10+ recommended.

```bash
python -m venv .venv
```

Windows:
```powershell
.venv\Scripts\activate
```

Install:
```bash
pip install -r requirements.txt
```

Copy `.env.example` to `.env`.

Run:
```bash
python cli.py
```

Try:
```text
Find me candidates with React and 3+ years experience
Compare the top 3 matches side by side
Why did John rank higher than Jane?
Add Python as a must-have
Make API testing a nice-to-have
Run deep screening
Give hire/no-hire recommendations
quit
```

## Milestone integration

Milestone 1 filesystem integration is in `tools/resume_search.py`.

Milestone 2 RAG integration is in `adapters/rag_adapter.py`. Set `USE_RAG=true` after implementing that adapter with your existing retriever/vector store.

## Assignment mapping

**Part A**
- State → `state.py`
- LangGraph → `matching_agent.py`
- Requirements → `tools/requirements.py`
- Candidate tools → `tools/candidate_tools.py`
- Search → `tools/resume_search.py`

**Part B**
- Natural language → `cli.py` / `conversation_node`
- Comparison → `compare_candidates`
- Explanation → ranking reasoning
- Refinement → conversational requirement updates

**Part C**
- Initial screen → top 10
- Deep screen → second round
- Final recommendation → hire/borderline/no-hire
- Explainability → strengths, gaps, reasoning and suggestions

This is an educational/reference hiring workflow; real hiring decisions should include human review.
