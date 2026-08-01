from dotenv import load_dotenv
load_dotenv()

from langgraph.graph import StateGraph, END
from state.schema import ResearchState
from agents.research_agent import research_node
from agents.fact_checker_agent import fact_checker_node
from agents.writer_agent import writer_node
from agents.critic_agent import critic_node


def route_after_critic(state: ResearchState) -> str:
    """
    Conditional edge: decide whether to loop back to writer or finish.
    """
    if state["approved"]:
        return "end"
    return "revise"


def build_graph():
    graph = StateGraph(ResearchState)

    # Register nodes
    graph.add_node("research", research_node)
    graph.add_node("fact_check", fact_checker_node)
    graph.add_node("write", writer_node)
    graph.add_node("critique", critic_node)

    # Define flow
    graph.set_entry_point("research")
    graph.add_edge("research", "fact_check")
    graph.add_edge("fact_check", "write")
    graph.add_edge("write", "critique")

    # Conditional edge: critique -> write (loop) OR critique -> END
    graph.add_conditional_edges(
        "critique",
        route_after_critic,
        {
            "revise": "write",
            "end": END,
        },
    )

    return graph.compile()


if __name__ == "__main__":
    app = build_graph()

    initial_state = {
        "query": input("Enter your research query: "),
        "sources": [],
        "verified_facts": [],
        "flagged_issues": [],
        "drafts": [],
        "critique_feedback": None,
        "approved": False,
        "iteration_count": 0,
        "max_iterations": 3,
    }

    final_state = app.invoke(initial_state)

    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(final_state["drafts"][-1])

    print("\n" + "=" * 60)
    print(f"Total iterations: {final_state['iteration_count']}")
    print(f"Approved: {final_state['approved']}")
    print("=" * 60)