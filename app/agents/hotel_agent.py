from app.tools.search_tool import search


def hotel_agent(destination: str, travelers: int, hotel_type: str, group_type: str = "", has_kids: bool = False):
    parts = []
    
    if has_kids:
        parts.append("family-friendly")
    elif group_type:
        parts.append(f"{group_type}-friendly")
    
    parts.append(hotel_type)
    parts.append(f"hotel cost per night in {destination} for {travelers} people")

    query = " ".join(parts)
    return search(query)