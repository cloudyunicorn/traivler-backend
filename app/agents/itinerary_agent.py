from app.core.llm import get_llm 

llm = get_llm()


def itinerary_agent(origin: str, destination: str, days: int, places: list, preferences: list):
    prompt = f"""
    Plan a {days}-day trip from {origin} to {destination}.

    Include:
    - Travel day allocation
    - Local travel time
    - Efficient route

    Places:
    {places}

    Preferences:
    {preferences}

    Make it personalized and balanced.
    """

    return llm.invoke(prompt)