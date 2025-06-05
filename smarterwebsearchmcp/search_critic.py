from datetime import datetime
from pydantic import BaseModel

from . import make_agent

today = datetime.today().strftime("%Y-%m-%d")

PROMPT = (
    "You critique search results. Given a topic, a search query and the search results, "
    "decide whether the search was successful or if the query should be revised. "
    "If the search results provides a satisfactory answer then the search is good enough. "
    f"Additional info: today is {today}."
)


class SearchItemCritique(BaseModel):
    is_good_enough: bool
    """Whether the search terms were good enough to get useful results."""

    critique: str | None = None
    """If the search was not successful, explain the problem and suggest improvements."""

    revised_query: str | None = None
    """If the search was not successful, provide revised search terms."""


search_critic_agent = make_agent(
    name="SearchPlanCriticAgent",
    instructions=PROMPT,
    output_type=SearchItemCritique,
)
