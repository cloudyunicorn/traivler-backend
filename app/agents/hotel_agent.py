from app.tools.search_tool import search
from datetime import datetime


def _get_season_context(start_date: str, destination: str) -> str:
    """Determine travel season from the start date for price context."""
    if not start_date:
        return ""
    
    try:
        dt = datetime.strptime(start_date, "%Y-%m-%d")
        month = dt.month
        month_name = dt.strftime("%B")
        
        # Determine general season
        if month in [12, 1, 2]:
            season = "winter/peak"
        elif month in [3, 4, 5]:
            season = "spring/shoulder"
        elif month in [6, 7, 8]:
            season = "summer/monsoon"
        else:
            season = "autumn/shoulder"
        
        return f"in {month_name} ({season} season)"
    except ValueError:
        return ""


async def hotel_agent(destination: str, travelers: int, hotel_type: str, group_type: str = "", has_kids: bool = False, start_date: str = "", end_date: str = ""):
    parts = []
    
    if has_kids:
        parts.append("family-friendly")
    elif group_type:
        parts.append(f"{group_type}-friendly")
    
    parts.append(hotel_type)
    parts.append(f"hotel cost per night in {destination} for {travelers} people")
    
    # Add season context for price-aware results
    season_ctx = _get_season_context(start_date, destination)
    if season_ctx:
        parts.append(season_ctx)
    
    if start_date and end_date:
        parts.append(f"check-in {start_date} check-out {end_date}")

    query = " ".join(parts)
    raw_results = await search(query)

    from app.core.llm import get_llm
    llm = get_llm()

    prompt = f"""You are a travel lodging expert. Based on the following raw web search results for hotel options in {destination}, extract and summarize the best hotel recommendations and average price ranges that match the criteria: "{query}".
    
    Raw Search Results:
    {raw_results}
    
    Provide a structured summary of:
    - Recommended hotel areas or specific hotel names suitable for {group_type or 'general'} travelers
    - Estimated average price range per night in the requested budget/type ({hotel_type})
    - Key amenities or reasons why they fit this group (e.g. family-friendly, kid-friendly)
    """
    
    response = await llm.ainvoke(prompt)
    return response.content