# ShopSage 🛍️ — Recommendation Agent

A shopping agent that asks clarifying questions, filters a product catalog
through a tool, and recommends options with clear reasoning — like a helpful
store assistant, built with **LangChain**, a custom **catalog tool**, and a
**Streamlit** front end.

## Why this project

Most "AI shopping" demos just dump a list of products. ShopSage instead
mimics how a good salesperson actually works: it asks what you need before
it recommends anything, it only talks about real products (never invented
ones), and it explains *why* it's suggesting something.

## Architecture

```
                     ┌─────────────────────┐
   User message ───► │   Streamlit UI       │
                     │  (app.py)            │
                     └─────────┬────────────┘
                               │ input + chat history
                               ▼
                     ┌─────────────────────┐
                     │  LangChain Agent     │
                     │  (agent.py)          │
                     │  - system prompt:    │
                     │    ask, then search  │
                     │  - tool-calling LLM  │
                     └─────────┬────────────┘
                               │ decides which tool to call
                               ▼
                     ┌─────────────────────┐
                     │   Catalog Tools      │
                     │  (tools.py)          │
                     │  - search_catalog    │
                     │  - compare_products  │
                     │  - rank_by_budget    │
                     └─────────┬────────────┘
                               │ reads
                               ▼
                     ┌─────────────────────┐
                     │  catalog.json        │
                     │  (20 sample products)│
                     └─────────────────────┘
```

**Flow:** the user describes what they want → the agent checks whether it
knows the category, budget, and use case → if not, it asks a clarifying
question → once it has enough info, it calls `search_catalog` → for a
shortlist, it can call `compare_products` and `rank_by_budget` → it replies
with a recommendation and the reasoning behind it.

## Project structure

```
shopsage/
├── data/
│   └── catalog.json        # sample product catalog (20 products, 5 categories)
├── tools.py                 # catalog tool: search, compare, rank
├── agent.py                  # LangChain agent + system prompt
├── app.py                    # Streamlit UI (chat + compare/rank tab)
├── requirements.txt
├── .env.example
└── .streamlit/config.toml    # theme
```

## Setup

1. **Clone and install dependencies**

   ```bash
   git clone <your-repo-url>
   cd shopsage
   python -m venv venv
   source venv/bin/activate        # Windows: venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. **Add your API key**

   Copy `.env.example` to `.env` and add either an OpenAI or Anthropic key —
   or just paste the key directly into the sidebar when the app is running.

3. **Run the app**

   ```bash
   streamlit run app.py
   ```

4. Open the local URL Streamlit prints, choose your provider in the sidebar,
   and start chatting — e.g. try:

   > "I need a laptop for video editing, budget around ₹1,00,000"

## How this meets the project outcomes

| Outcome | How it's implemented |
|---|---|
| **1. Recommend products using catalog filtering + stated reasoning** | `search_catalog` tool filters real data; the agent's system prompt requires it to explain *why* each recommendation fits (need, budget, trade-offs). |
| **2. Ask useful clarifying questions before recommending** | The system prompt instructs the agent to check for category/budget/use case and ask 1–2 short questions if missing, before calling any tool. |
| **3. Comparison view + budget-aware ranking** | `compare_products` and `rank_by_budget` tools are callable by the agent in chat, *and* exposed directly in a "Compare & Rank" Streamlit tab with a live budget slider. |

## Notes on the ranking algorithm

`rank_by_budget` blends two signals:
- **Value score** — rating per ₹1,000 spent (rewards good ratings at lower price).
- **Budget fit** — rewards prices that use the budget well without exceeding it,
  and penalizes options that go over budget proportionally to how far over they are.

Final score = `0.6 × value_score + 0.4 × budget_fit (scaled)`. This is a simple,
transparent heuristic — easy to explain in a viva, and easy to extend (e.g. add
a weight the user can tune).

## Possible extensions

- Swap the static `catalog.json` for a real product API or database.
- Add persistent memory (e.g. LangChain `ConversationBufferMemory` backed by SQLite)
  so ShopSage remembers a user's preferences across sessions.
- Add a "why not this one" explanation for rejected alternatives.
- Deploy on Streamlit Community Cloud for a shareable demo link.

## License

MIT — free to use and adapt for coursework.
