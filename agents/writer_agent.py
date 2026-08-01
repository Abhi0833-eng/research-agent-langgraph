import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from state.schema import ResearchState

load_dotenv()

llm = ChatGroq(
    model="llama-3.3-70b-versatile",
    temperature=0.4,
    api_key=os.getenv("GROQ_API_KEY"),
)

WRITER_PROMPT = """You are a research report writer. Write a clear, well-structured report answering the query below, using ONLY the verified facts provided. Do not invent information.

Query: {query}

Verified Facts:
{facts_text}

Known Issues / Caveats (mention briefly if relevant):
{issues_text}

{feedback_section}

Write a concise report (300-500 words) with a short intro, 2-4 organized sections, and a brief conclusion. Use markdown headers.
"""


def writer_node(state: ResearchState) -> ResearchState:
    """
    Drafts (or revises) the report using verified facts.
    If critique_feedback exists, incorporates it into the revision.
    """
    print(f"\n[Writer Agent] Drafting report (iteration {state['iteration_count'] + 1})...")

    facts_text = "\n".join(f"- {f}" for f in state["verified_facts"])
    issues_text = "\n".join(f"- {i}" for i in state["flagged_issues"]) or "None"

    feedback_section = ""
    if state.get("critique_feedback"):
        feedback_section = f"IMPORTANT - Address this feedback from the previous review:\n{state['critique_feedback']}"

    prompt = WRITER_PROMPT.format(
        query=state["query"],
        facts_text=facts_text,
        issues_text=issues_text,
        feedback_section=feedback_section,
    )

    response = llm.invoke(prompt)
    draft = response.content.strip()

    print(f"[Writer Agent] Draft complete ({len(draft.split())} words)")

    return {
        **state,
        "drafts": state["drafts"] + [draft],
        "iteration_count": state["iteration_count"] + 1,
    }