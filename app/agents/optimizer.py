from app.core.llm2 import get_llm2
from app.schemas.travel import TravelResponse
from app.core.llm import get_llm

llm = get_llm()
llm2 = get_llm2()


async def optimizer_agent(state):
    user_input = state.get("user_input", {})
    flights = state.get("flights", {})
    hotels = state.get("hotels", [])
    route_info = state.get("route_info", {})

    # Extract real flight pricing data
    per_person = flights.get("per_person", "N/A")
    currency = flights.get("currency", "INR")
    travelers = flights.get("total_travelers", user_input.get("travelers", 1))
    is_round_trip = flights.get("is_round_trip", False)
    is_open_jaw = flights.get("is_open_jaw", False)
    outbound_flight = flights.get("outbound_flight", {})
    return_flight = flights.get("return_flight", {})

    # Build flight pricing string for the LLM
    if isinstance(per_person, (int, float)):
        total_flight_cost = per_person * travelers
        flight_price_str = f"{currency} {per_person} per person, {currency} {total_flight_cost} total for {travelers} travelers"
    else:
        flight_price_str = str(per_person)

    # Build route string
    origin = route_info.get("origin_code", user_input.get("origin", ""))
    dest = route_info.get("destination_code", user_input.get("destination", ""))
    return_origin = route_info.get("return_origin_code", dest)
    
    if is_open_jaw:
        route_str = f"{origin} → {dest} (outbound), {return_origin} → {origin} (return) [Open-jaw]"
    elif is_round_trip:
        route_str = f"{origin} ↔ {dest} (Round trip)"
    else:
        route_str = f"{origin} → {dest}"

    # Build flight duration string
    duration_mins = outbound_flight.get("duration", 0) if outbound_flight else 0
    if duration_mins:
        hours = duration_mins // 60
        mins = duration_mins % 60
        duration_str = f"{hours}h {mins}m"
    else:
        duration_str = "Varies"

    prompt = f"""
    Create a structured travel plan from the following data.

    === FLIGHT DATA (USE THESE EXACT PRICES) ===
    Route: {route_str}
    Price per person: {currency} {per_person} ({'round trip' if is_round_trip else 'one way'})
    Total flight cost for {travelers} travelers: {flight_price_str}
    Duration: {duration_str}
    Airline: {outbound_flight.get('airline', 'Various') if outbound_flight else 'Various'}
    Transfers: {outbound_flight.get('transfers', 'N/A') if outbound_flight else 'N/A'}

    === HOTEL DATA ===  
    {hotels}

    === PLACES & ITINERARY ===
    Places: {state.get("places", [])}
    Itinerary: {state.get("itinerary", [])}

    === TRAVELER CONTEXT ===
    - Origin: {user_input.get("origin", "")}
    - Destination: {user_input.get("destination", "")}
    - Days: {user_input.get("days", 3)}
    - Start Date: {user_input.get("start_date", "N/A")}
    - End Date: {user_input.get("end_date", "N/A")}
    - Budget: {user_input.get("budget", "moderate")}
    - Group: {user_input.get("group_type", "general")} ({user_input.get("age_group", "")})
    - Intent: {user_input.get("travel_intent", "exploration")}
    - Pace: {user_input.get("trip_pace", "moderate")}
    - Kids: {user_input.get("has_kids", False)}
    - Fitness: {user_input.get("fitness_level", "moderate")}
    - Food: {", ".join(user_input.get("food_preferences", []))}
    - Avoids: {", ".join(user_input.get("must_avoid", []))}
    - Occasion: {user_input.get("special_occasion") or "none"}
    - Notes: {user_input.get("special_notes") or "none"}

    IMPORTANT RULES:
    1. For flights.avg_cost, use EXACTLY "{flight_price_str}" — do NOT make up prices
    2. For flights.route, use EXACTLY "{route_str}"
    3. For flights.duration, use "{duration_str}"
    4. For cost_breakdown.flights, use the EXACT total flight cost: "{flight_price_str}"
    5. For cost_breakdown.hotels, estimate based on hotel data × {user_input.get("days", 3)} nights — give a concrete {currency} amount
    6. For cost_breakdown.food, estimate daily food cost per person × {travelers} travelers × {user_input.get("days", 3)} days, based on {user_input.get("destination", "the destination")} local prices and budget level ({user_input.get("budget", "moderate")}). Give a concrete {currency} amount like "{currency} 15,000"
    7. For cost_breakdown.local_transport, estimate total cost for local taxis/metro/rideshare for {user_input.get("days", 3)} days at the destination for {travelers} people. Give a concrete {currency} amount
    8. For cost_breakdown.activities, estimate total sightseeing, entry tickets, tours, and experiences cost for {user_input.get("days", 3)} days for {travelers} people. Give a concrete {currency} amount
    9. For cost_breakdown.total_estimate, SUM all 5 categories (flights + hotels + food + transport + activities)
    10. ALL cost_breakdown values MUST be concrete amounts like "{currency} 25,000" — NEVER vague text like "varies" or "moderate pricing"

    Output JSON with:
    - summary (mention the personalization — group type, intent, occasion if any)
    - flights (route, avg_cost, duration)
    - hotels (avg_price_per_night, suggested_areas suitable for the group)
    - itinerary (list of days with activities tailored to the profile)
    - cost_breakdown (flights, hotels, food, local_transport, activities, total_estimate — ALL concrete {currency} amounts)
    """

    structured_llm = llm2.with_structured_output(TravelResponse)
    return await structured_llm.ainvoke(prompt)