"""
A tool to trigger a Keenable web search for a given query and return the top
results with their titles, links and snippets. Since the tool is stateless (i.e.
does not need access to agent state), it can be enabled for any agent, without
having to define a special method inside the agent:
`agent.enable_message(KeenableSearchTool)`

NOTE: No API key or extra install is needed. Without a key, the tool uses
Keenable's keyless public endpoint (rate limited per IP). To lift the limit,
set the KEENABLE_API_KEY environment variable in your `.env` file, e.g.
`KEENABLE_API_KEY=your_api_key_here`.

For more information, please refer to: https://keenable.ai/
"""

from typing import List, Tuple

from langroid.agent.tool_message import ToolMessage
from langroid.parsing.web_search import keenable_search


class KeenableSearchTool(ToolMessage):
    request: str = "keenable_search"
    purpose: str = """
            To search the web using Keenable and return up to <num_results>
            results relevant to the given <query>. When using this tool,
            ONLY show the required JSON, DO NOT SAY ANYTHING ELSE.
            Wait for the results of the web search, and then use them to
            compose your response.
            """
    query: str
    num_results: int

    def handle(self) -> str:
        """
        Conducts a search using Keenable based on the provided query
        and number of results by triggering a keenable_search.

        Returns:
            str: A formatted string containing the titles, links, and
                summaries of each search result, separated by two newlines.
        """
        search_results = keenable_search(self.query, self.num_results)
        # return Title, Link, Summary of each result, separated by two newlines
        results_str = "\n\n".join(str(result) for result in search_results)
        return f"""
        BELOW ARE THE RESULTS FROM THE WEB SEARCH. USE THESE TO COMPOSE YOUR RESPONSE:
        {results_str}
        """

    @classmethod
    def examples(cls) -> List["ToolMessage" | Tuple[str, "ToolMessage"]]:
        return [
            cls(
                query="When was the Llama2 Large Language Model (LLM) released?",
                num_results=3,
            ),
        ]
