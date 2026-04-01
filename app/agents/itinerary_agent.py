from typing import List, Optional
from app.core.llm import get_llm 

llm = get_llm()


async def itinerary_agent(origin: str, destination: str, days: int, places: list, preferences: list,
                      trip_pace: str = "moderate", fitness_level: str = "moderate",
                      has_kids: bool = False, group_type: str = "", travel_intent: str = "",
                      must_avoid: Optional[List] = None, special_occasion: str = "", special_notes: str = "",
                      destination_name: str = "", arrival_airport: str = "", departure_airport: str = ""):
    avoid_text = ", ".join(must_avoid or []) or "nothing specific"
    # Use full name in prompt to avoid ambiguous codes like "GB"
    display_destination = destination_name.strip() if destination_name and destination_name.strip() else destination

    prompt = f"""
    Plan a {days}-day trip from {origin} to {display_destination}.

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
    - IMPORTANT ROUTING: The traveler arrives at {arrival_airport or display_destination} on Day 1, and departs from {departure_airport or display_destination} on Day {days}. You MUST trace a logical map path starting in the arrival city and geographically progressing to end in the departure city!

    Make it personalized, balanced, and realistic.
    """

    return await llm.ainvoke(prompt)