from app.core.llm import get_llm

llm = get_llm()

def planner_agent(user_input: dict):
    prompt = f"""
    Plan a personalized travel trip.

    Input:
    {user_input}

    Extract:
    - origin
    - destination
    - Number of travelers
    - duration
    - budget
    - Preferences (e.g., beach, shopping, adventure)

    Break into:
    - flights
    - hotels
    - places
    - itinerary
    """

    return llm.invoke(prompt)