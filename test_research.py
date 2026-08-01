from agents.research_agent import research_node
from agents.fact_checker_agent import fact_checker_node

test_state = {
    "query": "latest advancements in agentic AI 2026",
    "sources": [],
    "verified_facts": [],
    "flagged_issues": [],
    "drafts": [],
    "critique_feedback": None,
    "approved": False,
    "iteration_count": 0,
    "max_iterations": 3,
}

state_after_research = research_node(test_state)
state_after_factcheck = fact_checker_node(state_after_research)

print("\n--- VERIFIED FACTS ---")
for fact in state_after_factcheck["verified_facts"]:
    print("-", fact)

print("\n--- FLAGGED ISSUES ---")
for issue in state_after_factcheck["flagged_issues"]:
    print("-", issue)
from agents.writer_agent import writer_node

state_after_writing = writer_node(state_after_factcheck)

print("\n--- DRAFT REPORT ---")
print(state_after_writing["drafts"][-1])

from agents.critic_agent import critic_node

state_after_critique = critic_node(state_after_writing)

print("\n--- CRITIQUE RESULT ---")
print("Approved:", state_after_critique["approved"])
print("Feedback:", state_after_critique["critique_feedback"])