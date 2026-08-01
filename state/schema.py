from typing import TypedDict, List, Optional
from langgraph.graph.message import add_messages
from typing import Annotated


class ResearchState(TypedDict):
    # The original user query
    query: str

    # Raw sources gathered by the research agent
    sources: List[dict]  # each dict: {"title": str, "url": str, "content": str}

    # Verified facts after fact-checking
    verified_facts: List[str]

    # Any contradictions or unverifiable claims flagged
    flagged_issues: List[str]

    # Draft versions of the report (we keep history for transparency)
    drafts: List[str]

    # Feedback from the critic agent on the latest draft
    critique_feedback: Optional[str]

    # Whether critic approved the current draft
    approved: bool

    # Safety guard against infinite critic <-> writer loops
    iteration_count: int
    max_iterations: int