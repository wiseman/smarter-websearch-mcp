from fastmcp import FastMCP
from smarterwebsearchmcp.manager import WebSearchManager

mcp = FastMCP("Smarter Web Search")

async def _perform_search(query: str) -> str:
    """Run the web search agents and return the results."""
    manager = WebSearchManager()
    # Plan and perform searches, reusing the manager internals
    plan = await manager._plan_searches(query)
    results = await manager._perform_searches(query, plan)
    output = []
    for item, text in results:
        output.append(f"# {item.query}\n{text}")
    return "\n\n".join(output)


@mcp.tool()
async def web_search(query: str) -> str:
    """Search the web using the built-in search agents."""
    return await _perform_search(query)


if __name__ == "__main__":
    mcp.run()
