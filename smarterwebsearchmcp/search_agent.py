from agents.model_settings import ModelSettings

from . import make_agent, web_search_tool

# Use web search to get context for a single search term and summarize it.
INSTRUCTIONS = (
    "You are a research assistant. Given search instructions and a search query, "
    "use web search to retrieve up-to-date context and produce a short summary "
    "of at most 300 words. Try to include 1-3 salient quotes from the source "
    "in the summary. Use the search instructions to guide your summarization. "
    "Return results in the format "
    "<url>URL</url><summary>SUMMARY</summary>"
)

search_agent = make_agent(
    name="SearchAgent",
    instructions=INSTRUCTIONS,
    tools=[web_search_tool.search_and_get_top_url_tool],
    model_settings=ModelSettings(tool_choice="required"),
)
