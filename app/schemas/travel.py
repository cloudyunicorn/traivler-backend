from pydantic import BaseModel, Field
from typing import List, Optional

class TravelRequest(BaseModel):
    origin: str = Field(..., min_length=2, max_length=100)
    destination: str = Field(..., min_length=2, max_length=150)
    start_date: Optional[str] = Field(None, max_length=10)  # YYYY-MM-DD
    end_date: Optional[str] = Field(None, max_length=10)     # YYYY-MM-DD
    days: int = Field(..., gt=0, le=30)
    budget: Optional[str] = Field(None, max_length=50)
    travelers: int = Field(..., gt=0, le=20)
    preferences: List[str] = Field(..., max_length=10)
    hotel_type: Optional[str] = Field("mid-range", max_length=50)
    transport_mode: Optional[str] = Field("flight", max_length=50)

    # Personalization fields
    travel_intent: str = Field(..., max_length=50)
    group_type: str = Field(..., max_length=30)
    age_group: str = Field(..., max_length=10)
    has_kids: bool = Field(...)
    fitness_level: str = Field(..., max_length=20)
    food_preferences: List[str] = Field(default_factory=list)
    trip_pace: str = Field(..., max_length=20)
    must_avoid: List[str] = Field(default_factory=list)
    special_occasion: Optional[str] = Field(None, max_length=50)
    special_notes: Optional[str] = Field(None, max_length=500)

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
    food: str
    local_transport: str
    activities: str
    total_estimate: str


class TravelResponse(BaseModel):
    summary: str
    flights: FlightInfo
    hotels: HotelInfo
    itinerary: List[DayPlan]
    cost_breakdown: CostBreakdown