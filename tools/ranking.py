import re
from typing import Dict, List

def extract_years(text: str) -> float:
    matches = re.findall(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)", text.lower())
    return max([float(x) for x in matches], default=0.0)

def rank_candidates(candidates: List[Dict], requirements: Dict) -> List[Dict]:
    must = requirements.get("must_have", [])
    nice = requirements.get("nice_to_have", [])
    min_years = float(requirements.get("min_years", 0))
    ranked = []

    for c in candidates:
        lower = c.get("resume_text", "").lower()
        matched_must = [s for s in must if s.lower() in lower]
        missing_must = [s for s in must if s.lower() not in lower]
        matched_nice = [s for s in nice if s.lower() in lower]
        years = extract_years(c.get("resume_text", ""))
        exp_ratio = 1.0 if not min_years else min(years / min_years, 1.0)

        score = (
            70 * (len(matched_must) / len(must) if must else 1.0)
            + 20 * (len(matched_nice) / len(nice) if nice else 0.0)
            + 10 * exp_ratio
        )

        c2 = dict(c)
        c2["score"] = round(score, 2)
        c2["strengths"] = matched_must + matched_nice
        c2["gaps"] = missing_must
        c2["reasoning"] = [
            f"Matched {len(matched_must)}/{len(must)} must-have skills.",
            f"Matched {len(matched_nice)}/{len(nice)} nice-to-have skills.",
            f"Estimated experience: {years:g} years; requirement: {min_years:g} years.",
        ]
        ranked.append(c2)

    return sorted(ranked, key=lambda x: x["score"], reverse=True)
