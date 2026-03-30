from typing import TypedDict, List, Dict


class TravelState(TypedDict):
    user_input: Dict
    plan: Dict
    route_info: Dict
    places: List[str]
    flights: List[str]
    hotels: List[str]
    itinerary: List[str]
    final_plan: str