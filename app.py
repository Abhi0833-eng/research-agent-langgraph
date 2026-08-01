from pathlib import Path
from typing import Any

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field

from main import build_graph


BASE_DIR = Path(__file__).resolve().parent
INDEX_FILE = BASE_DIR / "static" / "index.html"

app = FastAPI(
    title="Autonomous Research and Report Agent",
    description="Research, fact-check, write, and critique reports from a browser.",
    version="1.0.0",
)
graph = build_graph()


class ResearchRequest(BaseModel):
    query: str = Field(..., min_length=3, max_length=500)


class ResearchResponse(BaseModel):
    query: str
    report: str
    sources: list[dict[str, str]]
    verified_facts: list[str]
    flagged_issues: list[str]
    iterations: int
    approved: bool


@app.get("/", include_in_schema=False)
def index() -> FileResponse:
    return FileResponse(INDEX_FILE)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/research", response_model=ResearchResponse)
def research(request: ResearchRequest) -> ResearchResponse:
    query = request.query.strip()
    if len(query) < 3:
        raise HTTPException(status_code=422, detail="Query must contain at least 3 characters.")

    initial_state: dict[str, Any] = {
        "query": query,
        "sources": [],
        "verified_facts": [],
        "flagged_issues": [],
        "drafts": [],
        "critique_feedback": None,
        "approved": False,
        "iteration_count": 0,
        "max_iterations": 3,
    }

    try:
        final_state = graph.invoke(initial_state)
    except Exception as exc:
        raise HTTPException(
            status_code=502,
            detail="The research pipeline could not complete. Check the server logs and API keys.",
        ) from exc

    return ResearchResponse(
        query=query,
        report=final_state["drafts"][-1] if final_state["drafts"] else "",
        sources=[
            {"title": source.get("title", ""), "url": source.get("url", "")}
            for source in final_state["sources"]
        ],
        verified_facts=final_state["verified_facts"],
        flagged_issues=final_state["flagged_issues"],
        iterations=final_state["iteration_count"],
        approved=final_state["approved"],
    )
