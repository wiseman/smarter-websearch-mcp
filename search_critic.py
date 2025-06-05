# Compute today's date in YYYY-MM-DD format
from datetime import datetime

from pydantic import BaseModel

from . import make_agent

today = datetime.today().strftime("%Y-%m-%d")

PROMPT = (
    "You critique web search results. Given an original user query, "
    "the executed search query, and the search results, you decide whether "
    "the search was successful enough or needs to be revised to get better, "
    "more relevant results. Focus on relevance to the original user query. "
    f"Additional info: today is {today}."
)


class SearchCritique(BaseModel):
    is_good_enough: bool
    """Whether the search terms were good enough to get useful results."""

    critique: str | None = None
    """If the search was not successful, explain what the problem was and how
    to fix it by modifying the search terms."""

    revised_query: str | None = None
    """If the search was not successful, suggest 1-5 revised search terms."""


search_results_critic_agent = make_agent(
    name="SearchResultsCriticAgent",
    instructions=PROMPT,
    # model="o3-mini",
    output_type=SearchCritique,
)
