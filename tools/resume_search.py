from pathlib import Path
from typing import Dict, List
from config import RESUME_DIR, USE_RAG
from adapters.rag_adapter import search_resumes as rag_search

def _filesystem_search(query: str = "") -> List[Dict]:
    root = Path(RESUME_DIR)
    root.mkdir(parents=True, exist_ok=True)
    results = []
    for path in sorted(root.glob("*")):
        if not path.is_file() or path.suffix.lower() not in {".txt", ".md"}:
            continue
        text = path.read_text(encoding="utf-8", errors="ignore")
        results.append({
            "candidate_id": path.stem,
            "name": path.stem.replace("_", " ").title(),
            "resume_text": text,
            "source": str(path),
        })
    return results

def search_resumes(query: str = "", top_k: int = 100) -> List[Dict]:
    if USE_RAG:
        results = rag_search(query, top_k)
        if results:
            return results
    return _filesystem_search(query)[:top_k]
