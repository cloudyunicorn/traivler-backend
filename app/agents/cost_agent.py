import asyncio
from app.tools.search_tool import search
from app.core.llm2 import get_llm2
from app.schemas.travel import CostVerification


llm = get_llm2()


async def cost_agent(state) -> dict:
    """
    Post-optimizer agent that verifies and corrects cost estimates
    using real-world web search data. Falls back to optimizer costs on failure.
    """
    user_input = state.get("user_input", {})
    final_plan = state.get("final_plan", {})
    original_costs = final_plan.get("cost_breakdown", {})

    destination = user_input.get("destination_name", "").strip() or user_input.get("destination", "")
    hotel_type = user_input.get("hotel_type", "mid-range")
    budget = user_input.get("budget", "moderate")
    days = user_input.get("days", 3)
    travelers = user_input.get("travelers", 1)
    currency = user_input.get("currency", "USD")
    start_date = user_input.get("start_date", "")

    # Extract month/year for seasonal context
    month_str = ""
    if start_date and len(start_date) >= 7:
        try:
            from datetime import datetime
            dt = datetime.strptime(start_date[:10], "%Y-%m-%d")
            month_str = dt.strftime("%B %Y")
        except ValueError:
            pass

    print(f"\n{'='*60}")
    print(f"[COST AGENT] Verifying costs for {destination}")
    print(f"  hotel_type: {hotel_type} | budget: {budget} | currency: {currency}")
    print(f"  days: {days} | travelers: {travelers} | month: {month_str or 'N/A'}")
    print(f"  Original costs: {original_costs}")
    print(f"{'='*60}")

    # Run 4 parallel DuckDuckGo searches for real-world pricing
    search_queries = [
        f"{hotel_type} hotel average cost per night in {destination} {month_str} in {currency}",
        f"average meal food cost per person per day in {destination} in {currency}",
        f"local transport taxi metro daily cost in {destination} tourist in {currency}",
        f"popular tourist attractions entry fee costs in {destination} in {currency}",
    ]

    try:
        search_results = await asyncio.gather(
            *[search(q) for q in search_queries],
            return_exceptions=True
        )

        # Parse results, replacing exceptions with empty strings
        cost_data = []
        labels = ["hotels", "food", "transport", "activities"]
        for i, result in enumerate(search_results):
            if isinstance(result, Exception):
                print(f"  [COST AGENT] Search failed for {labels[i]}: {result}")
                cost_data.append("No data available")
            else:
                cost_data.append(str(result)[:600])

        hotel_data, food_data, transport_data, activity_data = cost_data

        prompt = f"""You are a travel cost verification agent. Your job is to compare cost estimates 
        against real-world search data and correct any that are clearly wrong.

        === CURRENT COST ESTIMATES (from AI optimizer) ===
        - Flights: {original_costs.get("flights", "N/A")}
        - Hotels: {original_costs.get("hotels", "N/A")}
        - Food: {original_costs.get("food", "N/A")}
        - Local Transport: {original_costs.get("local_transport", "N/A")}
        - Activities: {original_costs.get("activities", "N/A")}
        - Total: {original_costs.get("total_estimate", "N/A")}

        === REAL-WORLD SEARCH DATA ===
        Hotel pricing data: {hotel_data}
        Food pricing data: {food_data}
        Transport pricing data: {transport_data}
        Activity pricing data: {activity_data}

        === TRIP CONTEXT ===
        - Destination: {destination}
        - Duration: {days} days
        - Travelers: {travelers}
        - Hotel Type: {hotel_type}
        - Budget Level: {budget}
        - Currency: {currency}
        - Travel Period: {month_str or "Not specified"}

        === RULES ===
        1. NEVER modify the flights cost — it comes from a real API and is already accurate.
        Use EXACTLY: "{original_costs.get("flights", "N/A")}"
        2. For hotel_per_night: output the realistic average cost for ONE night at a {hotel_type} hotel in {destination}. Format: "{currency} X,XXX".
        3. For hotels: calculate as hotel_per_night × {days} nights. This MUST be mathematically consistent with hotel_per_night.
        4. For food: calculate as (real avg daily food cost per person) × {travelers} people × {days} days.
        5. For local_transport: calculate as (real daily transport cost) × {days} days for {travelers} people.
        6. For activities: estimate total sightseeing/entry fees for {days} days for {travelers} people based on search data.
        7. ALL amounts MUST be in {currency}. Format as "{currency} X,XXX" (e.g., "USD 1,200").
        8. total_estimate MUST be the arithmetic sum of flights + hotels + food + local_transport + activities.
        9. If search data is unavailable for a category, keep the optimizer's original estimate.
        10. Be realistic — don't inflate or deflate costs. Use the search data as ground truth.
        """

        structured_llm = llm.with_structured_output(CostVerification)
        corrected = await structured_llm.ainvoke(prompt)

        print(f"  [COST AGENT] Corrected costs: {corrected.dict()}")

        # Merge corrected costs into final_plan
        updated_plan = {**final_plan}
        updated_plan["cost_breakdown"] = {
            "flights": corrected.flights,
            "hotels": corrected.hotels,
            "food": corrected.food,
            "local_transport": corrected.local_transport,
            "activities": corrected.activities,
            "total_estimate": corrected.total_estimate,
        }

        # Keep Hotel Card consistent with cost breakdown
        if "hotels" in updated_plan and isinstance(updated_plan["hotels"], dict):
            updated_plan["hotels"]["avg_price_per_night"] = corrected.hotel_per_night

        return {"final_plan": updated_plan}

    except Exception as e:
        print(f"  [COST AGENT] Failed, falling back to optimizer costs: {e}")
        # Fallback: return state unchanged
        return {"final_plan": final_plan}
