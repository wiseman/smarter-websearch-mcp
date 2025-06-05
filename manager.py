from __future__ import annotations

import asyncio
import time
from collections.abc import Sequence

from rich.console import Console

# Attempting to import from OpenAI SDK - these are placeholders and might need adjustment
from openai.beta.threads.agents import Runner, RunResult # Placeholder, actual might differ
from openai.beta.threads.runs import custom_span # Placeholder
from openai.lib.traces import gen_trace_id, trace # Placeholder

from .planner_agent import SearchItem, SearchPlan, search_planner_agent
from .search_agent import web_search_agent
from .search_critic import SearchCritique, search_results_critic_agent
from printer import Printer


class WebSearchManager:
    """
    Orchestrates the full flow: planning, searching, sub‑analysis, writing, and verification.
    """

    def __init__(self) -> None:
        self.console = Console()
        self.printer = Printer(self.console)

    async def run(self, query: str) -> Sequence[str]:
        trace_id = gen_trace_id()
        with trace("Web search trace", trace_id=trace_id): # Updated trace name
            self.printer.update_item(
                "trace_id",
                f"View trace: https://platform.openai.com/traces/trace?trace_id={trace_id}",
                is_done=True,
                hide_checkmark=True,
            )
            self.printer.update_item(
                "start", "Starting web search...", is_done=True
            )
            search_plan: SearchPlan = await self._plan_searches(query)
            search_results = await self._perform_searches(query, search_plan)

            self.printer.end()

            print("\n\n===== SEARCH RESULTS =====\n\n")
            for i, result_content in enumerate(search_results):
                print(f"Result {i+1}:\n{result_content}\n---")
            return search_results

    async def _plan_searches(self, query: str) -> SearchPlan:
        self.printer.update_item("planning", "Planning searches...")
        result = await Runner.run(search_planner_agent, f"Query: {query}")
        self.printer.update_item(
            "planning",
            f"Will perform {len(result.final_output.searches)} searches",
            is_done=True,
        )
        # Print the search plan
        for i, item in enumerate(result.final_output.searches):
            self.printer.update_item(
                f"search_{i}",
                f"Search term: {item.query}\nReason: {item.reason}",
                is_done=True,
            )
        return result.final_output_as(SearchPlan)

    async def _perform_searches(
        self, query: str, search_plan: SearchPlan
    ) -> Sequence[str]:
        results: list[tuple[SearchItem, str]] = []
        with custom_span("Search the web"):
            self.printer.update_item("searching", "Searching...")
            tasks = [
                asyncio.create_task(self._search(item)) for item in search_plan.searches
            ]
            num_completed = 0
            for task in asyncio.as_completed(tasks):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
                self.printer.update_item(
                    "searching", f"Searching... {num_completed}/{len(tasks)} completed"
                )
            self.printer.update_item("refining", "Refining search results...")
            tasks = [
                asyncio.create_task(
                    self._refine_search_result(query, item, search_result)
                )
                for (item, search_result) in results
            ]
            results = []
            num_completed = 0
            for i, task in enumerate(asyncio.as_completed(tasks)):
                result = await task
                if result is not None:
                    results.append(result)
                num_completed += 1
                self.printer.update_item(
                    "refining", f"Refining... {i+1}/{len(tasks)} completed"
                )
            self.printer.update_item(
                "refining",
                f"Refined {len(results)} search results",
                is_done=True,
            )
            self.printer.mark_item_done("searching")
        return [search_result for (_, search_result) in results]

    async def _refine_search_result(
        self, query: str, item: SearchItem, search_result: str
    ) -> tuple[SearchItem, str] | None:
        input_data = f"Original query: {query}\nSearch terms: {item.query}\nSearch result: {search_result}"
        result = await Runner.run(search_results_critic_agent, input_data)
        critique: SearchCritique = result.final_output
        if critique.is_good_enough:
            self.printer.update_item(
                f"search_{str(item)}",
                f"{item.query} is good enough",
                is_done=True,
            )
            return (item, search_result)
        else:
            # Need to do a new search with the revised query
            self.printer.update_item(
                f"search_{str(item)}",
                f"{item.query} is not good enough, revising to {critique.revised_query}",
                is_done=True,
            )
            assert critique.revised_query is not None
            return await self._search(
                SearchItem(
                    reason=critique.critique or "No critique provided",
                    query=critique.revised_query,
                )
            )

    async def _search(
        self, item: SearchItem
    ) -> tuple[SearchItem, str] | None:
        input_data = f"Search term: {item.query}\nReason: {item.reason}"
        try:
            result = await Runner.run(web_search_agent, input_data)
            return (item, str(result.final_output))
        except Exception as e:
            self.printer.update_item(
                f"search_{str(item)}",
                f"Search term: {item.query} failed with error: {e}",
                is_done=True,
            )
            return None
