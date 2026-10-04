import re
from typing import Dict, List

KNOWN_SKILLS = [
    "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
    "Playwright", "Selenium", "Cypress", "Pytest", "Jest", "Cucumber",
    "REST API", "API Testing", "Postman", "Rest Assured", "SQL", "AWS",
    "Azure", "Docker", "Kubernetes", "Git", "Jenkins", "CI/CD", "Salesforce",
    "Tosca", "SDET", "Manual Testing", "Automation Testing"
]

def extract_requirements(jd: str) -> Dict:
    text = jd or ""
    lower = text.lower()
    must: List[str] = []
    nice: List[str] = []

    nice_section = re.search(
        r"(nice[- ]to[- ]have|preferred|good to have|bonus)(.*?)(?:\n\s*\n|$)",
        text, flags=re.I | re.S
    )
    nice_text = nice_section.group(2) if nice_section else ""

    for skill in KNOWN_SKILLS:
        if skill.lower() in lower:
            if skill.lower() in nice_text.lower():
                nice.append(skill)
            else:
                must.append(skill)

    years = 0.0
    for pattern in [
        r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)\s*(?:of)?\s*experience",
        r"experience\s*[:\-]?\s*(\d+(?:\.\d+)?)\s*\+?\s*(?:years?|yrs?)",
    ]:
        m = re.search(pattern, text, flags=re.I)
        if m:
            years = max(years, float(m.group(1)))

    return {
        "must_have": list(dict.fromkeys(must)),
        "nice_to_have": list(dict.fromkeys(nice)),
        "min_years": years,
        "raw_jd": text,
    }
