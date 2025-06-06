from __future__ import annotations

import asyncio
import sys
from collections.abc import Sequence
from typing import Callable

from agents import Runner, gen_trace_id, trace
from rich.console import Console

from .planner_agent import SearchItem, SearchPlan, planner_agent
from .search_agent import search_agent
from .search_critic import SearchItemCritique, search_critic_agent


class WebSearchManager:
    """Coordinates planning, searching and critique for generic web searches."""

    def __init__(self) -> None:
        self.console = Console()

    async def run(self, query_instructions: str) -> None:
        trace_id = gen_trace_id()
        with trace("web search trace", trace_id=trace_id):
            sys.stderr.write(f"Planning searches for: {query_instructions}")
            plan = await self._plan_searches(query_instructions)
            results = await self._perform_searches(query_instructions, plan)

        for item, text in results:
            sys.stderr.write(f"\n# {item.query}\n{text}\n")

    async def _plan_searches(self, query_instructions: str) -> SearchPlan:
        result = await Runner.run(planner_agent, f"Query: {query_instructions}")
        return result.final_output_as(SearchPlan)

    async def _perform_searches(
        self, query_instructions: str, search_plan: SearchPlan
    ) -> Sequence[tuple[SearchItem, str]]:
        tasks = [
            asyncio.create_task(self._search_and_refine(query_instructions, item))
            for item in search_plan.searches
        ]
        results: list[tuple[SearchItem, str]] = []
        for task in asyncio.as_completed(tasks):
            res = await task
            if res is not None:
                results.append(res)
        return results

    async def _search_and_refine(
        self, query_instructions: str, item: SearchItem
    ) -> tuple[SearchItem, str] | None:
        result = await self._search(query_instructions, item)
        if result is None:
            return None
        item, search_result = result
        input_data = f"Original query: {query_instructions}\nSearch terms: {item.query}\nSearch result: {search_result}"
        critique_result = await Runner.run(search_critic_agent, input_data)
        critique: SearchItemCritique = critique_result.final_output
        if critique.is_good_enough or not critique.revised_query:
            return item, search_result
        return await self._search(
            query_instructions,
            SearchItem(
                reason=critique.critique or "revised", query=critique.revised_query
            ),
        )

    async def _search(
        self, query_instructions: str, item: SearchItem
    ) -> tuple[SearchItem, str] | None:
        input_data = f"Search term: {item.query}\nReason: {item.reason}"
        try:
            result = await Runner.run(search_agent, input_data)
            return item, str(result.final_output)
        except Exception as e:
            sys.stderr.write(f"Search '{item.query}' failed: {e}")
            return None
