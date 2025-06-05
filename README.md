# smarterwebsearchmcp

This package contains tools and agents for orchestrating web searches using the OpenAI Agents SDK.

All code now lives in the `smarterwebsearchmcp` package:

```
smarterwebsearchmcp/
    __init__.py
    manager.py
    planner_agent.py
    search_agent.py
    search_critic.py
    web_search_tool.py
```

The repository also provides a small MCP server script that exposes the search
agents over the [FastMCP](https://pypi.org/project/fastmcp/) server:

```bash
fastmcp run -t sse mcp_server.py:mcp
```
