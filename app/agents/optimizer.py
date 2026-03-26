from app.schemas.travel import TravelResponse
from app.core.llm import get_llm

llm = get_llm()


def optimizer_agent(state):
    prompt = f"""
    Create a structured travel plan.

    Data:
    {state}

    Output JSON with:
    - summary
    - flights (route, avg_cost, duration)
    - hotels (avg_price_per_night, suggested_areas)
    - itinerary (list of days with activities)
    - cost_breakdown
    """

    structured_llm = llm.with_structured_output(TravelResponse)
    return structured_llm.invoke(prompt)