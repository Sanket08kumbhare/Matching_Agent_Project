import re
from pathlib import Path
from typing import Dict, List

from langchain_core.messages import AIMessage, HumanMessage
from langgraph.graph import END, START, StateGraph

from state import AgentState
from config import TOP_K
from tools.requirements import extract_requirements
from tools.resume_search import search_resumes
from tools.ranking import rank_candidates
from tools.candidate_tools import compare_candidates, generate_interview_questions

def parse_jd(state: AgentState) -> AgentState:
    jd = state.get("jd", "")
    if not jd:
        jd = Path("data/job_description.txt").read_text(encoding="utf-8")
    return {"jd": jd}

def extract_requirements_node(state: AgentState) -> AgentState:
    return {"job_requirements": extract_requirements(state["jd"])}

def search_resumes_node(state: AgentState) -> AgentState:
    req = state["job_requirements"]
    query = " ".join(req.get("must_have", []) + req.get("nice_to_have", []))
    return {"candidates": search_resumes(query, top_k=100)}

def rank_candidates_node(state: AgentState) -> AgentState:
    ranked = rank_candidates(state.get("candidates", []), state["job_requirements"])
    shortlist = ranked[:TOP_K]
    return {
        "candidate_shortlist": shortlist,
        "ranking_reasoning": {c["candidate_id"]: c.get("reasoning", []) for c in shortlist},
        "screening_round": 1,
    }

def generate_report_node(state: AgentState) -> AgentState:
    shortlist = state.get("candidate_shortlist", [])
    return {"report": {
        "summary": f"Found {len(shortlist)} candidates in the initial screen.",
        "top_candidates": [
            {
                "rank": i + 1,
                "name": c.get("name"),
                "score": c.get("score"),
                "strengths": c.get("strengths", []),
                "gaps": c.get("gaps", []),
                "reasoning": c.get("reasoning", []),
            }
            for i, c in enumerate(shortlist)
        ],
    }}

def human_feedback_node(state: AgentState) -> AgentState:
    feedback = state.get("human_feedback", "")
    history = list(state.get("conversation_history", []))
    if feedback:
        history.append({"role": "human_feedback", "content": feedback})
    return {"conversation_history": history, "pending_feedback": False}

def _find_candidate(text: str, shortlist: List[Dict]):
    for c in shortlist:
        if c.get("name", "").lower() in text.lower():
            return c
    return None

def handle_query(state: AgentState, query: str) -> AgentState:
    q = query.strip()
    lower = q.lower()
    shortlist = state.get("candidate_shortlist", [])

    if "compare" in lower:
        n = 3
        m = re.search(r"top\s+(\d+)", lower)
        if m:
            n = int(m.group(1))
        selected = shortlist[:n]
        comp = compare_candidates([c["candidate_id"] for c in selected], shortlist)
        lines = ["Candidate comparison:"]
        for c in comp["candidates"]:
            lines.append(
                f"- {c['name']}: {c['score']}/100 | "
                f"Strengths: {', '.join(c['strengths']) or 'None'} | "
                f"Gaps: {', '.join(c['gaps']) or 'None'}"
            )
        return {"response": "\n".join(lines)}

    if "why" in lower and "higher" in lower:
        if len(shortlist) >= 2:
            a, b = shortlist[0], shortlist[1]
            return {"response":
                f"{a['name']} ranked higher ({a['score']}) than {b['name']} ({b['score']}) "
                f"because {a['reasoning'][0].lower()} "
                f"Key strengths: {', '.join(a['strengths'][:5]) or 'none'}. "
                f"{b['name']} gaps: {', '.join(b['gaps'][:5]) or 'none'}."
            }
        return {"response": "I need at least two ranked candidates to explain the ranking."}

    if "interview" in lower and ("question" in lower or "screening" in lower):
        target = _find_candidate(q, shortlist) or (shortlist[0] if shortlist else None)
        if not target:
            return {"response": "No candidate is currently shortlisted."}
        qs = generate_interview_questions(target["candidate_id"], shortlist)
        return {"response": f"Interview questions for {target['name']}:\n" +
                "\n".join(f"{i+1}. {x}" for i, x in enumerate(qs))}

    if "deep" in lower or "second round" in lower:
        deep = []
        for c in shortlist:
            c2 = dict(c)
            c2["deep_analysis"] = (
                f"Deep review: validate {', '.join(c2.get('strengths', [])[:6])}; "
                f"probe gaps {', '.join(c2.get('gaps', [])[:4]) or 'none'}; "
                "verify project ownership, production impact, debugging and test strategy."
            )
            deep.append(c2)
        return {
            "deep_screened": deep,
            "screening_round": 2,
            "response": "Deep screening completed for the initial shortlist. Ask for final recommendations.",
        }

    if "hire" in lower or "final" in lower:
        source = state.get("deep_screened") or shortlist
        final = []
        for c in source:
            c2 = dict(c)
            score = float(c2.get("score", 0))
            gaps = c2.get("gaps", [])
            if score >= 75 and len(gaps) <= 1:
                rec = "Hire"
            elif score >= 55:
                rec = "Borderline / Additional Interview"
            else:
                rec = "No Hire"
            c2["recommendation"] = rec
            if rec.startswith("Borderline"):
                c2["improvement_suggestions"] = [
                    f"Demonstrate stronger evidence for {g}." for g in gaps
                ] or ["Provide stronger project-impact evidence."]
            final.append(c2)
        final.sort(key=lambda x: x.get("score", 0), reverse=True)
        return {
            "final_recommendations": final,
            "screening_round": 3,
            "response": "\n".join(
                f"{c['name']}: {c['recommendation']} ({c['score']}/100)" for c in final
            ),
        }

    if any(x in lower for x in ["add ", "remove ", "must-have", "must have", "nice-to-have", "nice to have"]):
        req = dict(state.get("job_requirements", {}))
        must = list(req.get("must_have", []))
        nice = list(req.get("nice_to_have", []))
        skills = [
            "Python", "Java", "JavaScript", "TypeScript", "React", "Angular", "Vue",
            "Playwright", "Selenium", "Cypress", "Pytest", "Cucumber", "API Testing",
            "Postman", "SQL", "AWS", "Azure", "Docker", "Kubernetes", "Git", "Jenkins",
            "CI/CD", "Salesforce", "Tosca"
        ]
        found = [s for s in skills if s.lower() in lower]
        for skill in found:
            if "remove" in lower:
                must = [x for x in must if x.lower() != skill.lower()]
                nice = [x for x in nice if x.lower() != skill.lower()]
            elif "nice" in lower:
                must = [x for x in must if x.lower() != skill.lower()]
                if skill not in nice:
                    nice.append(skill)
            else:
                if skill not in must:
                    must.append(skill)
                nice = [x for x in nice if x.lower() != skill.lower()]

        years_match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", lower)
        if years_match:
            req["min_years"] = float(years_match.group(1))
        req["must_have"] = must
        req["nice_to_have"] = nice

        ranked = rank_candidates(state.get("candidates", []), req)
        shortlist2 = ranked[:TOP_K]
        old = [c["candidate_id"] for c in shortlist]
        moved = [
            f"{c['name']}: new rank #{i+1}"
            for i, c in enumerate(shortlist2)
            if c["candidate_id"] in old and old.index(c["candidate_id"]) != i
        ]
        return {
            "job_requirements": req,
            "candidate_shortlist": shortlist2,
            "ranking_reasoning": {c["candidate_id"]: c.get("reasoning", []) for c in shortlist2},
            "response": (
                "Requirements updated and candidates re-ranked.\n"
                f"Must-have: {', '.join(must) or 'None'}\n"
                f"Nice-to-have: {', '.join(nice) or 'None'}\n" +
                ("Ranking changes:\n" + "\n".join(moved) if moved else "No ranking positions changed.")
            ),
        }

    if any(x in lower for x in ["find", "search", "candidates with"]):
        req = dict(state.get("job_requirements", {}))
        must = list(req.get("must_have", []))
        for skill in ["Python", "Java", "React", "TypeScript", "Playwright", "Selenium",
                      "API Testing", "SQL", "Tosca", "Salesforce"]:
            if skill.lower() in lower and skill not in must:
                must.append(skill)
        years_match = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*years?", lower)
        if years_match:
            req["min_years"] = float(years_match.group(1))
        req["must_have"] = must
        ranked = rank_candidates(state.get("candidates", []), req)
        return {
            "job_requirements": req,
            "candidate_shortlist": ranked[:TOP_K],
            "response": "Search criteria applied. Top matches:\n" + "\n".join(
                f"{i+1}. {c['name']} — {c['score']}/100"
                for i, c in enumerate(ranked[:TOP_K])
            ),
        }

    return {"response":
        "I can search candidates, compare matches, explain rankings, refine requirements, "
        "run deep screening, or generate final hire/no-hire recommendations."
    }

def conversation_node(state: AgentState) -> AgentState:
    q = state.get("user_query", "")
    result = handle_query(state, q)
    history = list(state.get("conversation_history", []))
    history.append({"role": "user", "content": q})
    if result.get("response"):
        history.append({"role": "assistant", "content": result["response"]})
    result["conversation_history"] = history
    return result

def build_graph():
    graph = StateGraph(AgentState)
    graph.add_node("parse_jd", parse_jd)
    graph.add_node("extract_requirements", extract_requirements_node)
    graph.add_node("search_resumes", search_resumes_node)
    graph.add_node("rank_candidates", rank_candidates_node)
    graph.add_node("generate_report", generate_report_node)
    graph.add_node("human_feedback", human_feedback_node)

    graph.add_edge(START, "parse_jd")
    graph.add_edge("parse_jd", "extract_requirements")
    graph.add_edge("extract_requirements", "search_resumes")
    graph.add_edge("search_resumes", "rank_candidates")
    graph.add_edge("rank_candidates", "generate_report")
    graph.add_edge("generate_report", "human_feedback")
    graph.add_edge("human_feedback", END)
    return graph.compile()

def run_initial_agent(jd: str = "") -> AgentState:
    return build_graph().invoke({
        "jd": jd,
        "messages": [],
        "conversation_history": [],
        "pending_feedback": False,
    })

if __name__ == "__main__":
    result = run_initial_agent()
    print(result["report"]["summary"])
    for row in result["report"]["top_candidates"]:
        print(row["rank"], row["name"], row["score"])
