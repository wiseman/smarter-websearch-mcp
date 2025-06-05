from datetime import datetime
from pydantic import BaseModel

from . import make_agent

today = datetime.today().strftime("%Y-%m-%d")

# Instructions for planning generic web searches.
PROMPT = (
    "You are a research planner. Given a user's request, "
    "produce a set of well-tailored web searches to gather the information needed."
    "Output between 5 and 15 queries to query for. "
    f"Additional info: today is {today}."
)


class SearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web search engine."""


class SearchPlan(BaseModel):
    searches: list[SearchItem]
    """A list of searches to perform."""


planner_agent = make_agent(
    name="SearchPlannerAgent",
    instructions=PROMPT,
    output_type=SearchPlan,
)
