import os
from dotenv import load_dotenv
from tavily import TavilyClient
from state.schema import ResearchState

load_dotenv()

tavily_client = TavilyClient(api_key=os.getenv("TAVILY_API_KEY"))


def research_node(state: ResearchState) -> ResearchState:
    """
    Takes the query from state, searches the web via Tavily,
    and returns updated state with sources populated.
    """
    query = state["query"]
    print(f"\n[Research Agent] Searching for: {query}")

    # Tavily search - returns top results with content snippets
    response = tavily_client.search(
        query=query,
        search_depth="advanced",
        max_results=5,
        include_answer=False,
    )

    sources = []
    for result in response.get("results", []):
        sources.append({
            "title": result.get("title", ""),
            "url": result.get("url", ""),
            "content": result.get("content", ""),
        })

    print(f"[Research Agent] Found {len(sources)} sources")

    return {
        **state,
        "sources": sources,
    }