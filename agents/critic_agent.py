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

CRITIC_PROMPT = """You are a strict editorial critic reviewing a research report draft.

Original Query: {query}

Draft Report:
{draft}

Verified Facts available (for reference, to check grounding):
{facts_text}

Evaluate the draft on:
1. Does it fully answer the original query?
2. Is it grounded only in the verified facts (no invented claims)?
3. Is it well-organized and clear?

Respond ONLY in valid JSON, no markdown, no preamble, in this exact format:
{{
  "approved": true or false,
  "feedback": "If not approved, specific actionable feedback on what to fix. If approved, empty string."
}}
"""


def critic_node(state: ResearchState) -> ResearchState:
    """
    Reviews the latest draft. Sets approved=True/False and critique_feedback.
    """
    print(f"\n[Critic Agent] Reviewing draft (iteration {state['iteration_count']})...")

    latest_draft = state["drafts"][-1]
    facts_text = "\n".join(f"- {f}" for f in state["verified_facts"])

    prompt = CRITIC_PROMPT.format(
        query=state["query"],
        draft=latest_draft,
        facts_text=facts_text,
    )

    response = llm.invoke(prompt)
    raw_output = response.content.strip()

    try:
        parsed = json.loads(raw_output)
        approved = parsed.get("approved", False)
        feedback = parsed.get("feedback", "")
    except json.JSONDecodeError:
        print("[Critic Agent] WARNING: Could not parse JSON, defaulting to approved=True to avoid infinite loop")
        approved = True
        feedback = ""

    # Safety: force approval if we've hit max iterations, regardless of critic's opinion
    if state["iteration_count"] >= state["max_iterations"]:
        print(f"[Critic Agent] Max iterations ({state['max_iterations']}) reached — force-approving")
        approved = True
        feedback = ""

    print(f"[Critic Agent] Approved: {approved}" + (f" | Feedback: {feedback}" if feedback else ""))

    return {
        **state,
        "approved": approved,
        "critique_feedback": feedback if not approved else None,
    }