from app.core.llm import get_llm
from langchain_core.output_parsers import JsonOutputParser
from pydantic import BaseModel, Field


class RouteDecision(BaseModel):
    destination_code: str = Field(description="Best IATA airport code to fly INTO at the destination")
    return_origin_code: str = Field(description="Best IATA airport code to fly BACK FROM on the return trip (can be same as destination_code for standard round trip, or different for open-jaw)")
    reasoning: str = Field(description="Brief explanation of the route choice")


llm = get_llm()
parser = JsonOutputParser(pydantic_object=RouteDecision)


async def route_agent(origin: str, destination: str, budget: str = "moderate") -> dict:
    """
    Uses an LLM to determine the best destination airport code and return
    departure airport for a trip. The user's origin airport is kept as-is.
    
    Returns:
        dict with origin_code, destination_code, return_origin_code, and reasoning.
    """

    prompt = f"""You are an expert travel route planner. Given a trip from an origin airport 
to a destination city/country/airport, determine:
1. The single best destination airport to FLY INTO
2. The best airport to FLY BACK FROM on the return trip

For most trips, the return airport will be the SAME as the destination airport (standard round trip).
However, for multi-city destinations or when the traveler's itinerary would naturally end in a different 
city than where they arrived, suggest a DIFFERENT return airport (open-jaw). For example:
- Trip to "Japan" might fly into NRT (Tokyo) and return from KIX (Osaka) if the itinerary flows Tokyo → Osaka
- Trip to "Bali" would likely be DPS → DPS (same airport, standard round trip)

Consider:
- Proximity to major tourist areas and city centers
- Flight availability and connectivity from the origin
- Cost efficiency (budget level: {budget})
- Whether an open-jaw route makes the itinerary more practical

Origin airport code: {origin}
Destination: {destination}

Respond in JSON format with exactly these fields:
- "destination_code": the best IATA airport code to fly INTO (3 letters)
- "return_origin_code": the best IATA airport code to fly BACK FROM (3 letters, same or different)
- "reasoning": a brief one-sentence explanation

{parser.get_format_instructions()}
"""

    response = await llm.ainvoke(prompt)
    
    try:
        parsed = parser.parse(response.content)
        return {
            "origin_code": origin,
            "destination_code": parsed["destination_code"],
            "return_origin_code": parsed["return_origin_code"],
            "reasoning": parsed["reasoning"]
        }
    except Exception as e:
        print(f"Route agent parsing error: {e}, falling back to raw destination")
        return {
            "origin_code": origin,
            "destination_code": destination,
            "return_origin_code": destination,
            "reasoning": f"Fallback: using '{destination}' for both legs."
        }
