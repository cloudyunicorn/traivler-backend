from pydantic import BaseModel, Field
from typing import List, Optional

class TravelRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=100)
    destination: str = Field(..., min_length=2, max_length=150)
    days: int = Field(..., gt=0, le=30)
    budget: Optional[str] = Field(None, max_length=50)
    travelers: int = Field(..., gt=0, le=20)
    preferences: List[str] = Field(..., max_length=10)
    hotel_type: Optional[str] = Field("mid-range", max_length=50)
    transport_mode: Optional[str] = Field("flight", max_length=50)

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