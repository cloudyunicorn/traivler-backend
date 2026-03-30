from typing import List, Optional
from app.tools.search_tool import search


async def search_agent(destination: str, preferences: list, travel_intent: str = "", must_avoid: Optional[List] = None, food_preferences: Optional[List] = None, group_type: str = ""):
    must_avoid = must_avoid or []
    food_preferences = food_preferences or []
    pref_text = " ".join(preferences)
    
    # Build a richer search query
    parts = []
    if group_type:
        parts.append(f"{group_type}-friendly")
    if travel_intent:
        parts.append(travel_intent)
    parts.append(pref_text)
    parts.append(f"places to visit in {destination}")
    
    if food_preferences:
        parts.append(f"with {' '.join(food_preferences)} food")
    
    if must_avoid:
        parts.append(f"avoiding {' '.join(must_avoid)}")

    query = " ".join(parts)
    return await search(query)