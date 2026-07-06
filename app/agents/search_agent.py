from typing import List, Optional
from app.tools.search_tool import search
from app.core.llm import get_llm

llm = get_llm()


async def search_agent(destination: str, preferences: list, travel_intent: str = "", must_avoid: Optional[List] = None, food_preferences: Optional[List] = None, group_type: str = "", destination_name: str = ""):
    must_avoid = must_avoid or []
    food_preferences = food_preferences or []
    pref_text = " ".join(preferences)

    # Use full destination name for search to avoid ambiguous codes (e.g. "GB" → "United Kingdom")
    search_destination = destination_name.strip() if destination_name and destination_name.strip() else destination

    # Build a richer search query
    parts = []
    if group_type:
        parts.append(f"{group_type}-friendly")
    if travel_intent:
        parts.append(travel_intent)
    parts.append(pref_text)
    parts.append(f"places to visit in {search_destination}")

    if food_preferences:
        parts.append(f"with {' '.join(food_preferences)} food")

    if must_avoid:
        parts.append(f"avoiding {' '.join(must_avoid)}")

    query = " ".join(parts)
    raw_results = await search(query)

    prompt = f"""You are a travel assistant. Based on the following raw web search results for places to visit in {search_destination}, extract and summarize the top places that match the traveler's query: "{query}".
    
    Raw Search Results:
    {raw_results}
    
    Provide a structured summary of the best places to visit, including:
    - Name of the place/attraction
    - Short description of what to do there
    - Why it fits the traveler's preferences (intent: {travel_intent}, group type: {group_type})
    - Any warnings (e.g., if it should be avoided based on must_avoid list: {must_avoid})
    """
    
    response = await llm.ainvoke(prompt)
    return response.content