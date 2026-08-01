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
    page_title="Research Desk | Grounded reports",
    page_icon="R",
    layout="wide",
)

st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Fraunces:opsz,wght@9..144,600;9..144,700&display=swap');
    .stApp { background: linear-gradient(135deg, rgba(206,77,45,.08), transparent 30%), #f7f4ed; }
    .block-container { max-width: 1180px; padding-top: 3.5rem; padding-bottom: 4rem; }
    h1, h2, h3 { font-family: 'Fraunces', Georgia, serif !important; color: #17212b !important; }
    p, label, .stMarkdown, .stCaption, button { font-family: 'DM Sans', Arial, sans-serif; }
    .hero-kicker { color: #ce4d2d; font: 700 12px/1.2 'DM Sans', sans-serif; letter-spacing: .16em; text-transform: uppercase; }
    .hero-title { margin: .5rem 0 .7rem; font: 700 clamp(2.8rem, 7vw, 5.8rem)/.93 'Fraunces', Georgia, serif; letter-spacing: -.03em; color: #17212b; }
    .hero-copy { max-width: 650px; color: #607080; font: 1.05rem/1.6 'DM Sans', sans-serif; }
    .section-label { color: #1e6865; font: 700 .75rem/1.2 'DM Sans', sans-serif; letter-spacing: .13em; text-transform: uppercase; }
    div[data-testid='stTextArea'] textarea { background: #fffdf8; border: 1px solid #d9d6cc; border-radius: 4px; color: #17212b; font-family: 'DM Sans', sans-serif; font-size: 1.05rem; }
    div[data-testid='stTextArea'] textarea:focus { border-color: #ce4d2d; box-shadow: 0 0 0 1px #ce4d2d; }
    div.stButton > button[kind='primary'] { background: #ce4d2d; border: 0; border-radius: 3px; color: white; font-weight: 700; padding: .75rem 1.3rem; }
    div.stButton > button[kind='primary']:hover { background: #a83b24; color: white; }
    .metric-card { background: #fffdf8; border: 1px solid #d9d6cc; border-radius: 4px; padding: 1rem 1.1rem; }
    .metric-value { color: #17212b; font: 700 1.7rem/1 'Fraunces', Georgia, serif; }
    .metric-label { color: #607080; font: .75rem/1.4 'DM Sans', sans-serif; margin-top: .35rem; }
    .source-card { background: #fffdf8; border-left: 3px solid #1e6865; margin: .5rem 0; padding: .7rem .9rem; }
    .source-card a { color: #9f351f; font-family: 'DM Sans', sans-serif; font-weight: 700; text-decoration: none; }
    </style>
    <div class="hero-kicker">Autonomous research desk</div>
    <div class="hero-title">Turn a question into a<br>grounded report.</div>
    <div class="hero-copy">Search the open web, verify the evidence, and shape it into a report reviewed by a critic agent.</div>
    """,
    unsafe_allow_html=True,
)

st.write("")
input_col, example_col = st.columns([1.55, 1], gap="large")
with input_col:
    st.markdown('<div class="section-label">Research question</div>', unsafe_allow_html=True)
    query = st.text_area(
        "Research question",
        placeholder="What is the condition of Gen Z in India?",
        height=145,
        label_visibility="collapsed",
    )
    generate = st.button(
        "Generate report",
        type="primary",
        disabled=len(query.strip()) < 3,
    )
with example_col:
    st.markdown('<div class="section-label">Start with a direction</div>', unsafe_allow_html=True)
    st.caption("Good questions are specific about a place, group, time, or decision.")
    st.info("Try: **How is remote work changing early-career jobs in India?**")
    st.info("Try: **What are the main risks and opportunities of agentic AI in 2026?**")

if generate:
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

    with st.status("Building your report...", expanded=True) as status:
        try:
            st.write("Searching for relevant sources")
            st.write("Checking claims against the evidence")
            st.write("Drafting and reviewing the report")
            final_state = build_graph().invoke(initial_state)
            status.update(label="Report ready", state="complete", expanded=False)
        except Exception:
            status.update(label="Research failed", state="error", expanded=True)
            st.error("The research pipeline could not complete. Check the configured API keys.")
            st.stop()

    st.divider()
    report_tab, facts_tab, sources_tab, issues_tab = st.tabs(
        ["Report", "Verified facts", "Sources", "Flagged issues"]
    )
    with report_tab:
        st.markdown(final_state["drafts"][-1])
        st.download_button(
            "Download report",
            data=final_state["drafts"][-1],
            file_name="research-report.md",
            mime="text/markdown",
        )
    with facts_tab:
        for fact in final_state["verified_facts"]:
            st.markdown(f"- {fact}")
    with sources_tab:
        for source in final_state["sources"]:
            title = source.get("title") or source.get("url")
            st.markdown(
                f'<div class="source-card"><a href="{source.get("url", "")}" target="_blank">{title}</a></div>',
                unsafe_allow_html=True,
            )
    with issues_tab:
        if final_state["flagged_issues"]:
            for issue in final_state["flagged_issues"]:
                st.warning(issue)
        else:
            st.success("No issues flagged.")

    st.write("")
    metric_cols = st.columns(3)
    metrics = [
        (str(len(final_state["sources"])), "sources consulted"),
        (str(final_state["iteration_count"]), "review iterations"),
        ("Approved" if final_state["approved"] else "Needs review", "editorial status"),
    ]
    for column, (value, label) in zip(metric_cols, metrics):
        with column:
            st.markdown(
                f'<div class="metric-card"><div class="metric-value">{value}</div><div class="metric-label">{label}</div></div>',
                unsafe_allow_html=True,
            )
