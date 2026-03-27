from app.schemas.travel import TravelResponse
from app.core.llm import get_llm

llm = get_llm()


def optimizer_agent(state):
    user_input = state.get("user_input", {})

    prompt = f"""
    Create a structured travel plan from the following data.

    Raw Data:
    {state}

    Traveler Context:
    - Group: {user_input.get("group_type", "general")} ({user_input.get("age_group", "")})
    - Intent: {user_input.get("travel_intent", "exploration")}
    - Pace: {user_input.get("trip_pace", "moderate")}
    - Kids: {user_input.get("has_kids", False)}
    - Fitness: {user_input.get("fitness_level", "moderate")}
    - Food: {", ".join(user_input.get("food_preferences", []))}
    - Avoids: {", ".join(user_input.get("must_avoid", []))}
    - Occasion: {user_input.get("special_occasion") or "none"}
    - Notes: {user_input.get("special_notes") or "none"}

    Output JSON with:
    - summary (mention the personalization — group type, intent, occasion if any)
    - flights (route, avg_cost, duration)
    - hotels (avg_price_per_night, suggested_areas suitable for the group)
    - itinerary (list of days with activities tailored to the profile)
    - cost_breakdown
    """

    structured_llm = llm.with_structured_output(TravelResponse)
    return structured_llm.invoke(prompt)