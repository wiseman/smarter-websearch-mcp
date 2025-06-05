import sys
from typing import Callable

from fastmcp import Context, FastMCP

from smarterwebsearchmcp.manager import WebSearchManager

mcp = FastMCP("Smarter Web Search")

async def _perform_search(query: str, ctx: Context) -> str:
    """Run the web search agents and return the results."""
    sys.stderr.write(f"Performing web search for: {query}\n")
    await ctx.report_progress(progress=0, total=2)
    manager = WebSearchManager()
    # Plan and perform searches, reusing the manager internals
    sys.stderr.write("Planning searches...\n")
    plan = await manager._plan_searches(query)
    await ctx.report_progress(progress=1, total=2)
    sys.stderr.write("Performing searches...\n")
    results = await manager._perform_searches(query, plan)
    sys.stderr.write(f"Search results: {len(results)} items found.\n")
    await ctx.report_progress(progress=2, total=2)
    output = []

    for item, text in results:
        output.append(f"# {item.query}\n{text}")
    await ctx.info("Search completed.")
    return "\n\n".join(output)


@mcp.tool()
async def web_search(query_instructions: str, ctx: Context) -> str:
    """Search the web. Pass the instructions or description of what
    you're looking for."""
    sys.stderr.write(f"Web search requested: {query_instructions}\n")
    await ctx.info("Starting web search...")
    return await _perform_search(query_instructions, ctx)


if __name__ == "__main__":
    mcp.run()
