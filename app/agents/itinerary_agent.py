from app.core.llm import get_llm 

llm = get_llm()


def itinerary_agent(origin: str, destination: str, days: int, places: list, preferences: list,
                     trip_pace: str = "moderate", fitness_level: str = "moderate",
                     has_kids: bool = False, group_type: str = "", travel_intent: str = "",
                     must_avoid: list = None, special_occasion: str = "", special_notes: str = ""):
    avoid_text = ", ".join(must_avoid or []) or "nothing specific"

    prompt = f"""
    Plan a {days}-day trip from {origin} to {destination}.

    Traveler Profile:
    - Group Type: {group_type or "general"}
    - Travel Intent: {travel_intent or "general exploration"}
    - Traveling with Kids: {has_kids}
    - Fitness Level: {fitness_level}
    - Trip Pace: {trip_pace} (relaxed = 2-3 activities/day, moderate = 3-4, packed = 5+)

    Include:
    - Travel day allocation
    - Local travel time between activities
    - Efficient route planning

    Places to consider:
    {places}

    Activity Preferences:
    {preferences}

    Must Avoid: {avoid_text}
    Special Occasion: {special_occasion or "none"}
    Additional Notes: {special_notes or "none"}

    Important guidelines:
    - If traveling with kids, prioritize family-friendly and safe activities
    - If fitness level is low, avoid strenuous hikes or long walks
    - If pace is relaxed, include free time and rest periods
    - If there's a special occasion, add a memorable experience for it
    - Strictly avoid anything in the must-avoid list

    Make it personalized, balanced, and realistic.
    """

    return llm.invoke(prompt)