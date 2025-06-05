# General Web Search MCP Tool

This project implements a general-purpose web search tool using the Model Context Protocol (MCP).
It utilizes an AI agentic workflow to refine search queries and process results.

## Features
-   Accepts a user query.
-   Plans a series of search queries.
-   Executes web searches.
-   Critiques and refines search results.
-   Returns a collection of search findings.
-   Exposes functionality via a `fastmcp` server.

## Prerequisites

*   Python 3.8+
*   `uv`: This project uses `uv` for package management. You can find installation instructions for `uv` [here](https://github.com/astral-sh/uv).
*   **OpenAI API Key**: You need an OpenAI API key for the agents to function. Set it as an environment variable: `export OPENAI_API_KEY='your_key_here'`.
*   **SearxNG Instance (Default)**: The `web_search_tool.py` is configured by default to use a local SearxNG instance at `http://localhost:8080/`. You'll need to either run one or modify the tool to use a different search provider.
*   **OpenAI SDK Imports**: The import paths for `Runner`, `RunResult`, `custom_span`, `gen_trace_id`, and `trace` in `manager.py` are placeholders (e.g., `from openai.beta.threads.agents import Runner, RunResult`). You may need to adjust these paths based on the specific version and structure of the OpenAI SDK you are using.

## Getting Started

1.  **Clone the repository:**
    ```bash
    git clone <repository_url>
    cd <repository_directory>
    ```

2.  **Create a virtual environment:**
    It's recommended to use a virtual environment.
    ```bash
    python -m venv .venv
    source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
    ```

3.  **Install dependencies using `uv`:**
    ```bash
    uv pip install -r requirements.txt
    ```

4.  **Run the MCP server:**
    The server uses Uvicorn.
    ```bash
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
    ```
    You should see output indicating the server is running, typically on `http://0.0.0.0:8000`.

5.  **Access the API:**
    *   Open your browser to `http://localhost:8000/docs` for the FastAPI Swagger UI, where you can interact with the `/search` endpoint.
    *   Or send a POST request directly, e.g., using curl:
        ```bash
        curl -X POST "http://localhost:8000/search" -H "Content-Type: application/json" -d '{"query": "your search query"}'
        ```

## Usage
(Details to be added once the `fastmcp` server is implemented)