---

# **Using Keenable Search with Langroid**

---

[Keenable](https://keenable.ai/) is a web search index built for AI agents.
`KeenableSearchTool` works **without an API key and without extra installs**:
it calls Keenable's keyless public endpoint, which is rate limited per IP.

---

## **1. (Optional) Set an API key**

To lift the per-IP limit, create a key at [keenable.ai](https://keenable.ai/)
and add it to your `.env` file:

```env
KEENABLE_API_KEY=<your_api_key>
```

When the variable is set, the tool uses the authenticated endpoint instead.

---

## **2. Use Keenable Search with Langroid**

```python
import langroid as lr
from langroid.agent.chat_agent import ChatAgent, ChatAgentConfig
from langroid.agent.tools.keenable_search_tool import KeenableSearchTool

# Configure the ChatAgent
config = ChatAgentConfig(
    name="search-agent",
    llm=lr.language_models.OpenAIGPTConfig(
        chat_model=lr.language_models.OpenAIChatModel.GPT4o
    ),
)

# Create the agent and enable the Keenable search tool
agent = ChatAgent(config)
agent.enable_message(KeenableSearchTool)

response = agent.llm_response(
    "What are the latest developments in quantum computing?"
)
print(response)
```

---

## **3. Direct Tool Usage**

```python
from langroid.agent.tools.keenable_search_tool import KeenableSearchTool

search_request = KeenableSearchTool(
    query="Latest breakthroughs in fusion energy",
    num_results=3,
)
print(search_request.handle())
```

Or call the underlying function, which returns `WebSearchResult` objects:

```python
from langroid.parsing.web_search import keenable_search

for result in keenable_search("Langroid multi-agent framework", num_results=3):
    print(result)
```

---

## **4. Full Example**

Run the web-search chatbot with Keenable as the provider:

```bash
python3 examples/basic/chat-search.py -p keenable
```

---
