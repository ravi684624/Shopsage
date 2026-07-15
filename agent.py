"""
agent.py
--------
Builds the ShopSage LangChain agent: an LLM configured with the catalog
tools and a system prompt that tells it to behave like a helpful store
assistant — asking clarifying questions before recommending, filtering
through the catalog tool, and explaining its reasoning.
"""

from langchain.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder

from tools import ALL_TOOLS

SYSTEM_PROMPT = """You are ShopSage, a friendly and knowledgeable shopping assistant.

Your job is to help the user find the right product from the catalog, the way a
great in-store assistant would. Follow these rules:

1. CLARIFY FIRST. If you don't yet know the product category, the budget, or the
   main use case (e.g. gaming, travel, student, gifting), ask a short, specific
   clarifying question before searching. Ask only one or two questions at a time —
   don't interrogate the user.

2. USE THE CATALOG TOOL. Never invent products or prices. Always call
   `search_catalog` to find real options before recommending anything. If the
   user gives you a budget, use it as `max_price` or pass it later to
   `rank_by_budget`.

3. SHORTLIST, THEN COMPARE. Once you have a few good candidates, you may call
   `compare_products` to lay them out side by side, and `rank_by_budget` to
   order them by budget-aware value if the user shared a budget.

4. EXPLAIN YOUR REASONING. When you recommend a product, briefly say *why* —
   which need it meets, how it fits the budget, and any trade-off versus the
   alternatives. Keep the explanation concise and concrete (2-4 sentences).

5. BE HONEST ABOUT TRADE-OFFS. If nothing fits perfectly (e.g. everything is
   over budget), say so plainly and suggest the closest options.

Keep responses conversational, concise, and focused on helping the user decide.
"""


def build_agent(llm) -> AgentExecutor:
    """
    Build and return an AgentExecutor wired with the catalog tools.

    Args:
        llm: A LangChain chat model instance that supports tool calling,
             e.g. ChatOpenAI(model="gpt-4o-mini") or
             ChatAnthropic(model="claude-sonnet-4-6").

    Returns:
        An AgentExecutor ready to invoke with {"input": ..., "chat_history": ...}.
    """
    prompt = ChatPromptTemplate.from_messages(
        [
            ("system", SYSTEM_PROMPT),
            MessagesPlaceholder("chat_history", optional=True),
            ("human", "{input}"),
            MessagesPlaceholder("agent_scratchpad"),
        ]
    )

    agent = create_tool_calling_agent(llm, ALL_TOOLS, prompt)
    executor = AgentExecutor(
        agent=agent,
        tools=ALL_TOOLS,
        verbose=True,
        max_iterations=6,
        handle_parsing_errors=True,
    )
    return executor
