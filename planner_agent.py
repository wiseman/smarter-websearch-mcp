# Compute today's date in YYYY-MM-DD format
from datetime import datetime

from pydantic import BaseModel

from . import make_agent

today = datetime.today().strftime("%Y-%m-%d")

# Generate a plan of searches to ground the financial analysis.
# For a given financial question or company, we want to search for
# recent news, official filings, analyst commentary, and other
# relevant background.
PROMPT = (
    "You are a search query planning assistant. Given a user's query, "
    "generate a set of diverse and effective web search queries to gather comprehensive information. "
    "Output between 3 and 10 search terms. "
    f"Additional info: today is {today}."
)


class SearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""


class SearchPlan(BaseModel):
    searches: list[SearchItem]
    """A list of searches to perform."""


search_planner_agent = make_agent(
    name="SearchPlannerAgent",
    instructions=PROMPT,
    # model="o3-mini",
    output_type=SearchPlan,
)
