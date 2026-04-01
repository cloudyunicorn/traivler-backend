from app.tools.search_tool import search
from app.tools.flight_search import fetch_flight_prices
from datetime import datetime, timedelta


async def flight_agent(
    origin: str, 
    destination: str, 
    travelers: int, 
    budget: str = "mid-range", 
    start_date: str = "", 
    end_date: str = "",
    return_origin: str = "",
    currency: str = "USD"
):
    # Use actual dates if provided, otherwise fallback
    if start_date:
        departure_date = start_date
    else:
        departure_date = (datetime.now() + timedelta(days=30)).strftime("%Y-%m")
    
    return_date = end_date  # May be empty
    
    # 1. Primary source: Aviasales (Travelpayouts) API — round trip
    flight_data = await fetch_flight_prices(
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        return_origin=return_origin,
        currency=currency
    )
    
    outbound = flight_data.get("outbound", [])
    return_flights = flight_data.get("return", [])
    is_round_trip = flight_data.get("is_round_trip", False)
    is_open_jaw = flight_data.get("is_open_jaw", False)
    
    selected_outbound = None
    selected_return = None
    search_context = ""

    if outbound:
        # 2. Selection logic based on budget
        if budget.lower() in ["cheap", "budget"]:
            selected_outbound = sorted(outbound, key=lambda x: x["price"])[0]
        elif budget.lower() in ["luxury", "premium"]:
            direct_flights = [f for f in outbound if f["transfers"] == 0]
            if direct_flights:
                selected_outbound = sorted(direct_flights, key=lambda x: x["price"])[-1]
            else:
                selected_outbound = sorted(outbound, key=lambda x: x["price"])[-1]
        else:
            selected_outbound = outbound[len(outbound)//2]
        
        # For open-jaw, also select a return flight
        if is_open_jaw and return_flights:
            if budget.lower() in ["cheap", "budget"]:
                selected_return = sorted(return_flights, key=lambda x: x["price"])[0]
            elif budget.lower() in ["luxury", "premium"]:
                direct_returns = [f for f in return_flights if f["transfers"] == 0]
                if direct_returns:
                    selected_return = sorted(direct_returns, key=lambda x: x["price"])[-1]
                else:
                    selected_return = sorted(return_flights, key=lambda x: x["price"])[-1]
            else:
                selected_return = return_flights[len(return_flights)//2]
    else:
        # 3. Fallback: DuckDuckGo search only when Aviasales has no data
        try:
            search_query = f"cheapest round trip flight from {origin} to {destination} {departure_date}"
            web_results = await search(search_query)
            search_context = str(web_results)[:500]
        except Exception as e:
            print(f"DuckDuckGo fallback search failed: {e}")
            search_context = "No flight data available"

    # Calculate per-person price
    # Use the pre-calculated total from flight_search (handles all cases correctly)
    total_price = flight_data.get("total_price")
    if total_price:
        per_person = round(total_price / 100) * 100  # Round to nearest 100
    elif selected_outbound:
        per_person = round(selected_outbound["price"] / 100) * 100
    else:
        per_person = "Variable (Check online)"

    # currency is passed as parameter (default USD)
    print(f"  [FLIGHT AGENT] per_person: {per_person} {currency} | travelers: {travelers} | round_trip: {is_round_trip} | open_jaw: {is_open_jaw}")
    
    result = {
        "per_person": per_person,
        "currency": currency,
        "total_travelers": travelers,
        "is_round_trip": is_round_trip,
        "is_open_jaw": is_open_jaw,
        "outbound_flight": selected_outbound,
        "return_flight": selected_return,
        "search_context": search_context,
        "more_options_link": selected_outbound.get("link") if selected_outbound else f"https://www.aviasales.com/search/{origin}{departure_date}28{destination}1"
    }
    
    if is_open_jaw:
        result["open_jaw_info"] = flight_data.get("open_jaw_info", {})
    
    return result