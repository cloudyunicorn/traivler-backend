from langgraph.graph import StateGraph
from app.state.travel_state import TravelState

from app.agents.planner import planner_agent
from app.agents.search_agent import search_agent
from app.agents.flight_agent import flight_agent
from app.agents.hotel_agent import hotel_agent
from app.agents.itinerary_agent import itinerary_agent
from app.agents.optimizer import optimizer_agent


def planner_node(state: TravelState):
    return {"plan": planner_agent(state["user_input"])}


def search_node(state: TravelState):
    data = state["user_input"]
    return {
        "places": search_agent(
            data["destination"],
            data["preferences"],
            travel_intent=data.get("travel_intent", ""),
            must_avoid=data.get("must_avoid", []),
            food_preferences=data.get("food_preferences", []),
            group_type=data.get("group_type", "")
        )
    }


def flight_node(state: TravelState):
    data = state["user_input"]

    return {
        "flights": flight_agent(
            data["origin"],
            data["destination"],
            data["travelers"]
        )
    }


def hotel_node(state: TravelState):
    data = state["user_input"]

    return {
        "hotels": hotel_agent(
            data["destination"],
            data["travelers"],
            data.get("hotel_type", "mid-range"),
            group_type=data.get("group_type", ""),
            has_kids=data.get("has_kids", False)
        )
    }


def itinerary_node(state: TravelState):
    data = state["user_input"]

    return {
        "itinerary": itinerary_agent(
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
            special_notes=data.get("special_notes", "")
        )
    }


def optimizer_node(state: TravelState):
    structured = optimizer_agent(state)

    return {
        "final_plan": structured.dict()
    }


graph = StateGraph(TravelState)

graph.add_node("planner", planner_node)
graph.add_node("search", search_node)
graph.add_node("flight", flight_node)
graph.add_node("hotel", hotel_node)
graph.add_node("itinerary", itinerary_node)
graph.add_node("optimizer", optimizer_node)

graph.set_entry_point("planner")

graph.add_edge("planner", "search")
graph.add_edge("planner", "flight")
graph.add_edge("planner", "hotel")

graph.add_edge("search", "itinerary")
graph.add_edge("flight", "itinerary")
graph.add_edge("hotel", "itinerary")

graph.add_edge("itinerary", "optimizer")

app_graph = graph.compile()