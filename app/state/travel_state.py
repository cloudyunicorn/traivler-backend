from typing import TypedDict, Dict, Any, Optional


class TravelState(TypedDict):
    user_input: Dict[str, Any]
    route_info: Optional[Dict[str, Any]]
    places: str
    flights: Dict[str, Any]
    hotels: str
    itinerary: str
    final_plan: Dict[str, Any]