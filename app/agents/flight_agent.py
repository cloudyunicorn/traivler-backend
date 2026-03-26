from app.tools.search_tool import search


def flight_agent(origin: str, destination: str, travelers: int):
    query = f"average flight cost per person from {origin} to {destination}"
    results = search(query)
    return {
        "per_person": results,
        "total_travelers": travelers
    }