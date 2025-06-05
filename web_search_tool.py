import asyncio
import json
import re

import httpx
from playwright.async_api import Error as PlaywrightError, async_playwright

from agents import function_tool


@function_tool
async def search_and_get_top_url_tool(query: str) -> str:
    """
    A tool to search the web for a given query and return the contents of the
    best matching URL.

    Args:
        query: The search query.

    Returns:
        The text of the web page that is the top result for the query.
    """
    return await search_and_get_top_url(query)


@function_tool
async def web_page_tool(url: str) -> str:
    """
    A tool to read a web page.

    Args:
        url: The URL of the web page to read.

    Returns:
        A string containing the title and cleaned text content of the main article
        on the page, or an error message if extraction failed.
    """
    return await get_readable_contents_of_url(url)


@function_tool
async def search_web_tool(query: str) -> str:
    """
    A tool to search the web for a given query.

    Args:
        query: The search query.

    Returns:
        A JSON string containing the search results.
    """
    return await search_web(query)


def squeeze_blank_lines(text: str) -> str:
    """Collapse runs of blank (all‑whitespace) lines to at most one blank
    line."""
    return re.sub(r"(?:[ \t]*\n){2,}", "\n\n", text)


DEFAULT_TIMEOUT_MS = 30000  # 30 seconds for page navigation/loading
READABILITY_CDN_URL = "https://cdn.skypack.dev/@mozilla/readability"


async def search_web(query: str) -> str:
    """
    A tool to search the web for a given query.

    Args:
        query: The search query.

    Returns:
        A JSON string containing the search results.
    """
    async with httpx.AsyncClient(follow_redirects=True, timeout=10.0) as client:
        print(f"Searching for: {query}")
        resp = await client.get(
            # My searxng instance
            "http://localhost:8080/search",
            params={"q": query, "format": "json", "safesearch": "0"},
            headers={"Accept": "application/json"},
        )
        resp.raise_for_status()
        return resp.text


async def get_readable_contents_of_url(url: str) -> str:
    """
    Read a web page using a browser, dynamically load Readability.js from a CDN,
    extract the main article content, and return the cleaned text content.

    Args:
        url: The URL of the web page to read.

    Returns:
        A string containing the title and cleaned text content of the main article
        on the page, or an error message if extraction failed.
    """
    if not url or not (url.startswith("http://") or url.startswith("https://")):
        return f"Error: Invalid URL provided: '{url}'. Please provide a full URL starting with http:// or https://."
    # JavaScript to execute in the page context
    # Uses dynamic import() to load Readability from CDN
    script_to_execute = f"""
        async () => {{ // Must be async because of await import
            try {{
                // Dynamically import the Readability class from the CDN
                // Using destructuring assignment to get the Readability class directly
                const {{ Readability }} = await import('{READABILITY_CDN_URL}');

                // Clone the document to avoid modifying the original (recommended by Readability)
                const documentClone = document.cloneNode(true);

                // Basic check if Readability was imported successfully
                if (typeof Readability !== 'function') {{
                    return {{ error: true, message: 'Failed to load Readability class from CDN: {READABILITY_CDN_URL}' }};
                }}

                // Instantiate Readability and parse the cloned document
                const reader = new Readability(documentClone);
                const article = reader.parse();

                // Return the parsed article object
                // Handle cases where parse() might return null
                return article || {{ error: true, message: 'Readability.parse() returned null.' }};

            }} catch (e) {{
                console.error('Error executing Readability script:', e); // Log in browser console
                return {{
                    error: true,
                    message: 'Error executing Readability script: ' + e.toString() + (e.stack ? '\\nStack: ' + e.stack : '')
                }};
            }}
        }}
    """

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            context = await browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
                java_script_enabled=True,
                ignore_https_errors=True,  # Be cautious in production
                bypass_csp=True,
            )
            page = await context.new_page()

            try:
                await page.goto(
                    url, timeout=DEFAULT_TIMEOUT_MS, wait_until="domcontentloaded"
                )
                # Wait longer for heavy SPAs if needed
                await page.wait_for_load_state(
                    "networkidle", timeout=DEFAULT_TIMEOUT_MS / 2
                )
            except PlaywrightError as e:
                await browser.close()
                # Limit error message length
                error_message = f"Error navigating to {url}: {e}"
                return error_message[:1000]

            # Execute the async script in the page context
            result = await page.evaluate(script_to_execute)

            await browser.close()

            # Process the result (same logic as before)
            if result and isinstance(result, dict):
                if result.get("error"):
                    error_detail = result.get(
                        "message", "Unknown Readability execution error"
                    )
                    return f"Error executing Readability.js on {url}: {error_detail}"[
                        :1000
                    ]

                elif result.get("content") and result.get("textContent"):
                    title = result.get("title", "No Title Found")
                    content = result.get(
                        "textContent", ""
                    ).strip()

                    if not content:
                        return f"URL: {url}\nTitle: {title}\n\nContent: (Readability extracted empty content)"
                    cleaned_content = "\n".join(
                        line.strip() for line in content.splitlines()
                    )
                    cleaned_content = squeeze_blank_lines(cleaned_content)
                    # Optional: Truncate long content (adjust MAX_LENGTH as needed for your LLM)
                    # MAX_LENGTH = 15000
                    # if len(cleaned_content) > MAX_LENGTH:
                    #    cleaned_content = cleaned_content[:MAX_LENGTH] + "... (truncated)"

                    output = (
                        f"URL: {url}\nTitle: {title}\n\nContent:\n{cleaned_content}"
                    )
                    return output
                else:
                    # This case might be hit if parse() returned null and our handling caught it
                    return f"Error: Readability.js parsing returned unexpected result for {url}. Missing 'content' or 'textContent', or parse() failed."
            else:
                # Handle cases where JS execution failed more fundamentally
                return f"Error: Failed to execute Readability script or received invalid result for {url}. Result was: {str(result)[:200]}"
    except PlaywrightError as e:
        return f"Error during Playwright operation for {url}: {e}"[:1000]
    except Exception as e:
        import traceback

        traceback.print_exc()
        return f"An unexpected error occurred while processing {url}: {e}"[:1000]


async def search_and_get_top_url(query: str) -> str:
    """
    Search the web for a given query and return the first URL found.

    Args:
        query: The search query.

    Returns:
        The first URL found in the search results.
    """
    # Perform a web search using the search_web function
    search_results = json.loads(await search_web(query))
    url = search_results["results"][0]["url"]
    text = await get_readable_contents_of_url(url)
    return text


# --- Example Usage (for testing) ---
async def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description="Simple web search utility")
    parser.add_argument(
        "query",
        nargs="+",
        help="Search query to submit",
    )
    parser.add_argument(
        "--agent",
        action="store_true",
        help="Use the manager to orchestrate agents for the search",
    )
    args = parser.parse_args()

    query = " ".join(args.query)
    if args.agent:
        from .manager import WebSearchManager

        manager = WebSearchManager()
        await manager.run(query)
    else:
        print(await search_and_get_top_url(query))


if __name__ == "__main__":
    try:
        asyncio.get_running_loop()
        asyncio.create_task(main())
    except RuntimeError:
        asyncio.run(main())
