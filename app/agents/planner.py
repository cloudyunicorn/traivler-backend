from app.core.llm import get_llm

llm = get_llm()

async def planner_agent(user_input: dict):
    avoid_text = ", ".join(user_input.get("must_avoid", [])) or "nothing specific"
    food_text = ", ".join(user_input.get("food_preferences", [])) or "no specific preference"

    prompt = f"""
    Plan a highly personalized travel trip.

    Trip Details:
    - Origin: {user_input.get("origin")}
    - Destination: {user_input.get("destination")}
    - Duration: {user_input.get("days")} days
    - Budget: {user_input.get("budget", "moderate")}
    - Travelers: {user_input.get("travelers")}
    - Preferences: {", ".join(user_input.get("preferences", []))}

    Traveler Profile:
    - Travel Intent: {user_input.get("travel_intent")}
    - Group Type: {user_input.get("group_type")}
    - Age Group: {user_input.get("age_group")}
    - Traveling with Kids: {user_input.get("has_kids", False)}
    - Fitness Level: {user_input.get("fitness_level")}
    - Trip Pace: {user_input.get("trip_pace")}

    Food Preferences: {food_text}
    Must Avoid: {avoid_text}
    Special Occasion: {user_input.get("special_occasion") or "none"}
    Special Notes: {user_input.get("special_notes") or "none"}

    Based on this profile, break the plan into:
    - flights
    - hotels (suitable for the group type)
    - places (matching intent, avoiding blacklisted items)
    - itinerary (paced according to trip_pace and fitness_level)
    """

    return await llm.ainvoke(prompt)