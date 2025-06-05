from agents.model_settings import ModelSettings

from . import web_search_tool
from . import make_agent

# Given a search term, use web search to pull back a brief summary.
# Summaries should be concise but capture the main financial points.
INSTRUCTIONS = (
    "You are a research assistant. Given a search query, "
    "use web search to retrieve relevant information and produce a concise summary of at most 300 words. "
    "Focus on the key information that directly answers or relates to the search query."
)

web_search_agent = make_agent(
    name="WebSearchAgent",
    instructions=INSTRUCTIONS,
    tools=[web_search_tool.search_and_get_top_url_tool],
    model_settings=ModelSettings(tool_choice="required"),
)
