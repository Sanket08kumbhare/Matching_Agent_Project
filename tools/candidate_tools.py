from typing import Dict, List

def compare_candidates(candidate_ids: list, candidates: List[Dict]) -> Dict:
    selected = [
        c for cid in candidate_ids
        for c in candidates
        if c.get("candidate_id") == cid or c.get("name", "").lower() == str(cid).lower()
    ]
    return {"candidates": [
        {
            "candidate_id": c.get("candidate_id"),
            "name": c.get("name"),
            "score": c.get("score", 0),
            "strengths": c.get("strengths", []),
            "gaps": c.get("gaps", []),
            "reasoning": c.get("reasoning", []),
        } for c in selected
    ]}

def generate_interview_questions(candidate_id: str, candidates: List[Dict]) -> List[str]:
    candidate = next(
        (c for c in candidates if c.get("candidate_id") == candidate_id
         or c.get("name", "").lower() == candidate_id.lower()), None
    )
    if not candidate:
        return [f"Candidate '{candidate_id}' was not found."]

    skills = candidate.get("strengths", [])[:6]
    gaps = candidate.get("gaps", [])[:3]
    questions = [f"Walk me through a project where you used {s}." for s in skills]
    questions += [
        f"This role requires {g}. How would you demonstrate or develop this capability?"
        for g in gaps
    ]
    questions += [
        "Describe a difficult defect you found and how you proved root cause.",
        "How do you decide what should be automated versus tested manually?",
        "How would you improve a flaky automation suite?",
    ]
    return questions[:10]
