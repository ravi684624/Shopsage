"""
app.py
------
Streamlit front-end for ShopSage.

Two views:
  1. "Chat with ShopSage" — a conversational agent that asks clarifying
     questions, searches the catalog, and recommends products with reasoning.
  2. "Compare & Rank" — a manual panel where the user can pick products from
     the catalog and instantly see a side-by-side comparison and a
     budget-aware ranking, without needing an LLM call.
"""

import json
import os

import pandas as pd
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage

from tools import CATALOG, compare_products, rank_by_budget

st.set_page_config(page_title="ShopSage", page_icon="🛍️", layout="wide")

# ---------------------------------------------------------------------------
# Sidebar: model + API key configuration
# ---------------------------------------------------------------------------
st.sidebar.title("🛍️ ShopSage settings")

provider = st.sidebar.selectbox("LLM provider", ["Groq", "Google", "OpenAI", "Anthropic"])

if provider == "Groq":
    api_key = st.sidebar.text_input(
        "Groq API key", type="password", value=os.environ.get("GROQ_API_KEY", "")
    )
    model_name = st.sidebar.text_input("Model", value="llama-3.3-70b-versatile")
elif provider == "Google":
    api_key = st.sidebar.text_input(
        "Google API key", type="password", value=os.environ.get("GOOGLE_API_KEY", "")
    )
    model_name = st.sidebar.text_input("Model", value="gemini-3.5-flash")
elif provider == "OpenAI":
    api_key = st.sidebar.text_input(
        "OpenAI API key", type="password", value=os.environ.get("OPENAI_API_KEY", "")
    )
    model_name = st.sidebar.text_input("Model", value="gpt-4o-mini")
else:
    api_key = st.sidebar.text_input(
        "Anthropic API key", type="password", value=os.environ.get("ANTHROPIC_API_KEY", "")
    )
    model_name = st.sidebar.text_input("Model", value="claude-sonnet-4-6")

st.sidebar.markdown("---")
st.sidebar.caption(
    "ShopSage never invents products — every recommendation comes from the "
    "catalog tool. Your API key is only used for this session and is not stored."
)

# ---------------------------------------------------------------------------
# Build the agent lazily, once a key is provided
# ---------------------------------------------------------------------------
@st.cache_resource(show_spinner=False)
def get_executor(provider: str, api_key: str, model_name: str):
    from agent import build_agent

    if provider == "Groq":
        from langchain_groq import ChatGroq

        llm = ChatGroq(model=model_name, api_key=api_key, temperature=0.3)
    elif provider == "Google":
        from langchain_google_genai import ChatGoogleGenerativeAI

        llm = ChatGoogleGenerativeAI(model=model_name, google_api_key=api_key, temperature=0.3)
    elif provider == "OpenAI":
        from langchain_openai import ChatOpenAI

        llm = ChatOpenAI(model=model_name, api_key=api_key, temperature=0.3)
    else:
        from langchain_anthropic import ChatAnthropic

        llm = ChatAnthropic(model=model_name, api_key=api_key, temperature=0.3)

    return build_agent(llm)


st.title("ShopSage 🛍️ — your reasoning shopping assistant")

tab_chat, tab_compare = st.tabs(["💬 Chat with ShopSage", "📊 Compare & Rank"])

# ---------------------------------------------------------------------------
# TAB 1: Chat
# ---------------------------------------------------------------------------
with tab_chat:
    if "history" not in st.session_state:
        st.session_state.history = []  # list of HumanMessage / AIMessage

    for msg in st.session_state.history:
        role = "user" if isinstance(msg, HumanMessage) else "assistant"
        with st.chat_message(role):
            st.markdown(msg.content)

    user_input = st.chat_input("Tell ShopSage what you're shopping for...")

    if user_input:
        if not api_key:
            st.warning(f"Please add your {provider} API key in the sidebar first.")
        else:
            st.session_state.history.append(HumanMessage(content=user_input))
            with st.chat_message("user"):
                st.markdown(user_input)

            executor = get_executor(provider, api_key, model_name)
            with st.chat_message("assistant"):
                with st.spinner("Thinking through the catalog..."):
                    result = executor.invoke(
                        {
                            "input": user_input,
                            "chat_history": st.session_state.history[:-1],
                        }
                    )
                    answer = result["output"]
                    st.markdown(answer)

            st.session_state.history.append(AIMessage(content=answer))

    if st.button("Reset conversation"):
        st.session_state.history = []
        st.rerun()

# ---------------------------------------------------------------------------
# TAB 2: Manual Compare & Rank (no LLM required — pure tool logic)
# ---------------------------------------------------------------------------
with tab_compare:
    st.subheader("Browse the catalog")

    df = pd.DataFrame(CATALOG)
    categories = ["All"] + sorted(df["category"].unique().tolist())
    col1, col2 = st.columns([1, 3])
    with col1:
        chosen_cat = st.selectbox("Filter by category", categories)

    filtered_df = df if chosen_cat == "All" else df[df["category"] == chosen_cat]
    st.dataframe(
        filtered_df[["id", "name", "brand", "category", "price", "rating", "features"]],
        use_container_width=True,
        hide_index=True,
    )

    st.subheader("Build a shortlist")
    shortlist = st.multiselect(
        "Pick 2-4 products to compare",
        options=df["id"] + " — " + df["name"],
    )
    shortlist_ids = [s.split(" — ")[0] for s in shortlist]

    if len(shortlist_ids) >= 2:
        st.markdown("#### Side-by-side comparison")
        comp_rows = df[df["id"].isin(shortlist_ids)].copy()
        comp_rows["features"] = comp_rows["features"].apply(lambda f: ", ".join(f))
        st.table(
            comp_rows[["id", "name", "brand", "price", "rating", "features"]].set_index("id")
        )

        st.markdown("#### Budget-aware ranking")
        budget = st.slider("Your budget (₹)", min_value=500, max_value=150000, value=30000, step=500)
        ranking_text = rank_by_budget.invoke({"product_ids": shortlist_ids, "budget": budget})
        st.code(ranking_text, language=None)
    else:
        st.info("Select at least 2 products above to see a comparison and ranking.")
