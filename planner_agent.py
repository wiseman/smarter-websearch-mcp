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
    "You are a financial research planner. Given a request for financial analysis, "
    "produce a set of web searches to gather the context needed. Aim for recent "
    "headlines, earnings calls or 10‑K snippets, analyst commentary, and industry background. "
    "Output between 5 and 15 search terms to query for. "
    f"Additional info: today is {today}."
)


class FinancialSearchItem(BaseModel):
    reason: str
    """Your reasoning for why this search is relevant."""

    query: str
    """The search term to feed into a web (or file) search."""


class FinancialSearchPlan(BaseModel):
    searches: list[FinancialSearchItem]
    """A list of searches to perform."""


planner_agent = make_agent(
    name="FinancialPlannerAgent",
    instructions=PROMPT,
    # model="o3-mini",
    output_type=FinancialSearchPlan,
)
