from langgraph.graph import StateGraph
from app.state.travel_state import TravelState

from app.agents.planner import planner_agent
from app.agents.search_agent import search_agent
from app.agents.route_agent import route_agent
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.itinerary_agent import itinerary_agent
from app.agents.optimizer import optimizer_agent
from app.agents.cost_agent import cost_agent


async def planner_node(state: TravelState):
    return {"plan": await planner_agent(state["user_input"])}


async def search_node(state: TravelState):
    data = state["user_input"]
    return {
        "places": await search_agent(
            data["destination"],
            data["preferences"],
            travel_intent=data.get("travel_intent", ""),
            must_avoid=data.get("must_avoid", []),
            food_preferences=data.get("food_preferences", []),
            group_type=data.get("group_type", ""),
            destination_name=data.get("destination_name", "")
        )
    }


async def flight_node(state: TravelState):
    """Route Agent + Flight Agent combined in one node to keep fan-in symmetric."""
    data = state["user_input"]

    # Step 1: Route agent determines best destination airport
    route = await route_agent(
        origin=data["origin"],
        destination=data["destination"],
        budget=data.get("budget", "moderate")
    )

    # Step 2: Flight agent searches using resolved airport codes
    origin = route.get("origin_code", data["origin"])
    destination = route.get("destination_code", data["destination"])

    return {
        "route_info": route,
        "flights": await flight_agent(
            origin,
            destination,
            data["travelers"],
            budget=data.get("budget", "mid-range"),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", ""),
            return_origin=route.get("return_origin_code", destination),
            currency=data.get("currency", "USD")
        )
    }


async def hotel_node(state: TravelState):
    data = state["user_input"]

    return {
        "hotels": await hotel_agent(
            data["destination"],
            data["travelers"],
            data.get("hotel_type", "mid-range"),
            group_type=data.get("group_type", ""),
            has_kids=data.get("has_kids", False),
            start_date=data.get("start_date", ""),
            end_date=data.get("end_date", "")
        )
    }


async def itinerary_node(state: TravelState):
    data = state["user_input"]

    return {
        "itinerary": await itinerary_agent(
            data["origin"],
            data["destination"],
            data["days"],
            state["places"],
            data["preferences"],
            trip_pace=data.get("trip_pace", "moderate"),
            fitness_level=data.get("fitness_level", "moderate"),
            has_kids=data.get("has_kids", False),
            group_type=data.get("group_type", ""),
            travel_intent=data.get("travel_intent", ""),
            must_avoid=data.get("must_avoid", []),
            special_occasion=data.get("special_occasion", ""),
            special_notes=data.get("special_notes", ""),
            destination_name=data.get("destination_name", "")
        )
    }


async def optimizer_node(state: TravelState):
    structured = await optimizer_agent(state)

    return {
        "final_plan": structured.dict()
    }


async def cost_node(state: TravelState):
    return await cost_agent(state)


graph = StateGraph(TravelState)

graph.add_node("planner", planner_node)
graph.add_node("search", search_node)
graph.add_node("flight", flight_node)
graph.add_node("hotel", hotel_node)
graph.add_node("itinerary", itinerary_node)
graph.add_node("optimizer", optimizer_node)
graph.add_node("cost", cost_node)

graph.set_entry_point("planner")

# After planner: 3 symmetric parallel branches (all 2 hops to itinerary)
graph.add_edge("planner", "search")
graph.add_edge("planner", "flight")
graph.add_edge("planner", "hotel")

# All 3 branches converge into itinerary
graph.add_edge("search", "itinerary")
graph.add_edge("flight", "itinerary")
graph.add_edge("hotel", "itinerary")

graph.add_edge("itinerary", "optimizer")
graph.add_edge("optimizer", "cost")

app_graph = graph.compile()