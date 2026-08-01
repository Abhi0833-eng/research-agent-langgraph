import os
import json
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state.schema import ResearchState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY"),
)

FACT_CHECK_PROMPT = """You are a fact-checking agent. You are given a research query and a list of sources.

Query: {query}

Sources:
{sources_text}

Your job:
1. Extract factual claims that are supported by at least one source. List them as clear, standalone statements.
2. Flag any contradictions between sources, or claims that seem unsupported/unverifiable.

Respond ONLY in valid JSON, no markdown, no preamble, in this exact format:
{{
  "verified_facts": ["fact 1", "fact 2", ...],
  "flagged_issues": ["issue 1", "issue 2", ...]
}}
"""


def fact_checker_node(state: ResearchState) -> ResearchState:
    """
    Cross-verifies claims across sources using the LLM.
    Populates verified_facts and flagged_issues in state.
    """
    print("\n[Fact-Checker Agent] Verifying sources...")

    sources_text = "\n\n".join(
        f"Source: {s['title']} ({s['url']})\nContent: {s['content'][:800]}"
        for s in state["sources"]
    )

    prompt = FACT_CHECK_PROMPT.format(query=state["query"], sources_text=sources_text)

    response = llm.invoke(prompt)
    raw_output = response.content.strip()

    try:
        parsed = json.loads(raw_output)
        verified_facts = parsed.get("verified_facts", [])
        flagged_issues = parsed.get("flagged_issues", [])
    except json.JSONDecodeError:
        print("[Fact-Checker Agent] WARNING: Could not parse JSON, raw output:")
        print(raw_output)
        verified_facts = []
        flagged_issues = ["JSON parsing failed - see logs"]

    print(f"[Fact-Checker Agent] Verified {len(verified_facts)} facts, flagged {len(flagged_issues)} issues")

    return {
        **state,
        "verified_facts": verified_facts,
        "flagged_issues": flagged_issues,
    }