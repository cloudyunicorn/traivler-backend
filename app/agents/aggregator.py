def aggregate_data(state):
    return {
        "places": state["places"],
        "flights": state["flights"],
        "hotels": state["hotels"],
        "itinerary": state["itinerary"],
    }