from pydantic import BaseModel
from typing import List, Optional

class TravelRequest(BaseModel):
    origin: str
    destination: str
    days: int
    budget: Optional[str]
    travelers: int              
    preferences: List[str]
    hotel_type: Optional[str] = "mid-range"    # e.g., budget, mid-range, luxury
    transport_mode: Optional[str] = "flight"

class FlightInfo(BaseModel):
    route: str
    avg_cost: str
    duration: str


class HotelInfo(BaseModel):
    avg_price_per_night: str
    suggested_areas: List[str]


class DayPlan(BaseModel):
    day: int
    activities: List[str]


class CostBreakdown(BaseModel):
    flights: str
    hotels: str
    total_estimate: str


class TravelResponse(BaseModel):
    summary: str
    flights: FlightInfo
    hotels: HotelInfo
    itinerary: List[DayPlan]
    cost_breakdown: CostBreakdown