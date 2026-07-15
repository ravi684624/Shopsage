"""
tools.py
--------
Defines the "Catalog Tool" set for ShopSage: functions the LangChain agent
can call to search, filter, compare, and rank products from the catalog.

Each tool is a plain Python function wrapped with LangChain's @tool decorator,
so the LLM can decide *when* and *how* to call them (tool-calling / function-calling).
"""

import json
from pathlib import Path
from typing import List, Optional

from langchain_core.tools import tool

# Resolves to the absolute path of the directory containing tools.py
BASE_DIR = Path(__file__).resolve().parent
CATALOG_PATH = BASE_DIR / "data" / "catalog.json"

# Added explicit utf-8 encoding to prevent system-dependent character issues
with open(CATALOG_PATH, "r", encoding="utf-8") as f:
    CATALOG: List[dict] = json.load(f)


def _format_products(products: List[dict]) -> str:
    """Turn a list of product dicts into a readable string for the LLM."""
    if not products:
        return "No products matched those filters."
    lines = []
    for p in products:
        lines.append(
            f"- [{p['id']}] {p['name']} ({p['brand']}) — ₹{p['price']:,} | "
            f"rating {p['rating']}/5 | category: {p['category']} | "
            f"features: {', '.join(p['features'])} | "
            f"use cases: {', '.join(p['use_cases'])}"
        )
    return "\n".join(lines)


@tool
def search_catalog(
    category: Optional[str] = None,
    min_price: Optional[float] = None,
    max_price: Optional[float] = None,
    brand: Optional[str] = None,
    min_rating: Optional[float] = None,
    keyword: Optional[str] = None,
) -> str:
    """
    Search and filter the product catalog.

    Use this tool once you know at least the product category the user wants
    (e.g. "Laptop", "Headphones", "Smartphone", "Smartwatch", "Backpack").
    You can optionally narrow results with price range, brand, minimum rating,
    or a free-text keyword that is matched against features, use cases, and
    the product description (e.g. "gaming", "travel", "student").

    Args:
        category: Product category to filter by (case-insensitive).
        min_price: Minimum price in rupees.
        max_price: Maximum price in rupees.
        brand: Brand name to filter by (case-insensitive).
        min_rating: Minimum star rating (0-5).
        keyword: Free-text keyword matched against features/use_cases/description.

    Returns:
        A formatted list of matching products with id, name, price, rating,
        features and use cases.
    """
    results = CATALOG

    if category:
        results = [p for p in results if p["category"].lower() == category.lower()]
    if brand:
        results = [p for p in results if p["brand"].lower() == brand.lower()]
    if min_price is not None:
        results = [p for p in results if p["price"] >= min_price]
    if max_price is not None:
        results = [p for p in results if p["price"] <= max_price]
    if min_rating is not None:
        results = [p for p in results if p["rating"] >= min_rating]
    if keyword:
        kw = keyword.lower()
        results = [
            p for p in results
            if kw in " ".join(p["features"]).lower()
            or kw in " ".join(p["use_cases"]).lower()
            or kw in p["description"].lower()
        ]

    return _format_products(results)


@tool
def compare_products(product_ids: List[str]) -> str:
    """
    Build a side-by-side comparison of two or more products by their IDs.

    Use this after search_catalog has returned candidates and the user wants
    to compare a shortlist (e.g. compare 2-4 laptops on price, rating, and features).

    Args:
        product_ids: List of product IDs to compare, e.g. ["LP001", "LP003"].

    Returns:
        A formatted comparison table as text.
    """
    products = [p for p in CATALOG if p["id"] in product_ids]
    if not products:
        return "None of those product IDs were found in the catalog."

    header = f"{'ID':<7}{'Name':<22}{'Price':<10}{'Rating':<8}{'Key Features'}"
    rows = [header, "-" * len(header)]
    for p in products:
        rows.append(
            f"{p['id']:<7}{p['name']:<22}₹{p['price']:<9,}{p['rating']:<8}"
            f"{', '.join(p['features'][:3])}"
        )
    return "\n".join(rows)


@tool
def rank_by_budget(product_ids: List[str], budget: float) -> str:
    """
    Rank a shortlist of products against a user's budget, balancing value
    (rating per rupee) with how close the price is to the stated budget.

    Use this once you have a shortlist of candidate product IDs (from
    search_catalog) and the user has told you their budget.

    Args:
        product_ids: List of candidate product IDs to rank.
        budget: The user's maximum budget in rupees.

    Returns:
        Products ranked from best to worst budget-aware value, with a short
        reason for each ranking.
    """
    products = [p for p in CATALOG if p["id"] in product_ids]
    if not products:
        return "None of those product IDs were found in the catalog."

    scored = []
    for p in products:
        over_budget = p["price"] > budget
        # Value score: rating per 1000 rupees spent (higher is better)
        value_score = p["rating"] / (p["price"] / 1000)
        # Budget fit: how close price is to budget without exceeding it
        if over_budget:
            budget_fit = -abs(p["price"] - budget) / budget  # penalty
        else:
            budget_fit = 1 - (budget - p["price"]) / budget  # reward using budget well
        final_score = value_score * 0.6 + budget_fit * 10 * 0.4
        scored.append((final_score, p, over_budget))

    scored.sort(key=lambda x: x[0], reverse=True)

    lines = []
    for rank, (score, p, over_budget) in enumerate(scored, start=1):
        note = "within budget" if not over_budget else f"₹{p['price'] - budget:,.0f} over budget"
        lines.append(
            f"{rank}. [{p['id']}] {p['name']} — ₹{p['price']:,} ({note}), "
            f"rating {p['rating']}/5, value score {score:.2f}"
        )
    return "\n".join(lines)


ALL_TOOLS = [search_catalog, compare_products, rank_by_budget]