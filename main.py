import asyncio
import uvicorn
from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List, Sequence

from manager import WebSearchManager # Assuming manager.py is in the same directory

# Initialize FastAPI app
app = FastAPI(
    title="General Web Search MCP Server",
    description="An MCP server for performing general web searches using an agentic workflow.",
    version="0.1.0",
)

# Initialize the WebSearchManager
# This assumes WebSearchManager can be instantiated without arguments or with defaults
search_manager = WebSearchManager()

class SearchQueryInput(BaseModel):
    query: str = Field(..., description="The web search query.", example="What are the latest advancements in AI?")

class SearchResultsOutput(BaseModel):
    results: Sequence[str] = Field(..., description="A list of search result summaries or content snippets.")

@app.post("/search", response_model=SearchResultsOutput)
async def perform_search(input_data: SearchQueryInput) -> SearchResultsOutput:
    """
    Accepts a search query, processes it through a planner, searcher, and critic agent,
    and returns a list of search results.
    """
    query = input_data.query
    # The WebSearchManager.run method is async
    search_results = await search_manager.run(query=query)
    return SearchResultsOutput(results=search_results)

@app.get("/")
async def root():
    return {"message": "Welcome to the General Web Search MCP Server. Use the /search endpoint to make queries."}

# It's good practice to allow running the server directly for development/testing
if __name__ == "__main__":
    # Note: For production, you'd typically use a process manager like Gunicorn or Supervisor
    # uvicorn.run(app, host="0.0.0.0", port=8000)
    # For the purpose of this tool, we'll print a message on how to run it.
    print("FastAPI MCP server defined. To run this server:")
    print("1. Ensure you have uvicorn and fastapi installed: pip install uvicorn fastapi")
    print("2. Run the server using Uvicorn: uvicorn main:app --reload")
    print("   (Or your preferred ASGI server)")
