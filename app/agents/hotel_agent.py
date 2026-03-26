from app.tools.search_tool import search


def hotel_agent(destination: str, travelers: int, hotel_type: str):
    query = f"{hotel_type} hotel cost per night in {destination} for {travelers} people"
    
    return search(query)