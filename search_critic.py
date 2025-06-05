# Compute today's date in YYYY-MM-DD format
from datetime import datetime

from pydantic import BaseModel

from . import make_agent

today = datetime.today().strftime("%Y-%m-%d")

PROMPT = (
    "You critique search plans that are meant to gather relevant information for"
    "financial analysis. Given a topic, a search query, and the search results, "
    "you decide whether the search was successful or needs to be revised to get "
    "better results. "
    f"Additional info: today is {today}."
)


class FinanicalSearchItemCritique(BaseModel):
    is_good_enough: bool
    """Whether the search terms were good enough to get useful results."""

    critique: str | None = None
    """If the search was not successful, explain what the problem was and how
    to fix it by modifying the search terms."""

    revised_query: str | None = None
    """If the search was not successful, suggest 5-15 revised search terms."""


search_critic_agent = make_agent(
    name="FinancialPlanCriticAgent",
    instructions=PROMPT,
    # model="o3-mini",
    output_type=FinanicalSearchItemCritique,
)
