import os

import streamlit as st


for secret_name in ("TAVILY_API_KEY", "GROQ_API_KEY", "LANGSMITH_TRACING"):
    try:
        if secret_name in st.secrets:
            os.environ[secret_name] = str(st.secrets[secret_name])
    except (FileNotFoundError, KeyError):
        pass

from main import build_graph


st.set_page_config(
    page_title="Research Desk",
    page_icon="R",
    layout="wide",
)

st.title("Autonomous Research Desk")
st.caption("Search, verify, write, and critique a research report.")

query = st.text_area(
    "Research question",
    placeholder="What is the condition of Gen Z in India?",
    height=130,
)

if st.button("Generate report", type="primary", disabled=len(query.strip()) < 3):
    initial_state = {
        "query": query.strip(),
        "sources": [],
        "verified_facts": [],
        "flagged_issues": [],
        "drafts": [],
        "critique_feedback": None,
        "approved": False,
        "iteration_count": 0,
        "max_iterations": 3,
    }

    with st.status("Researching and reviewing...", expanded=True) as status:
        try:
            final_state = build_graph().invoke(initial_state)
            status.update(label="Report ready", state="complete", expanded=False)
        except Exception:
            status.update(label="Research failed", state="error", expanded=True)
            st.error("The research pipeline could not complete. Check the configured API keys.")
            st.stop()

    st.markdown(final_state["drafts"][-1])
    st.divider()
    left, right = st.columns(2)
    with left:
        st.subheader("Verified facts")
        for fact in final_state["verified_facts"]:
            st.markdown(f"- {fact}")
    with right:
        st.subheader("Flagged issues")
        if final_state["flagged_issues"]:
            for issue in final_state["flagged_issues"]:
                st.markdown(f"- {issue}")
        else:
            st.write("No issues flagged.")

    st.subheader("Sources")
    for source in final_state["sources"]:
        title = source.get("title") or source.get("url")
        st.markdown(f"- [{title}]({source.get('url', '')})")

    st.caption(
        f"{len(final_state['sources'])} sources · "
        f"{final_state['iteration_count']} review iterations · "
        f"Approved: {final_state['approved']}"
    )
