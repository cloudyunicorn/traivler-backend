import httpx
from typing import List
from app.config import settings


async def fetch_flight_prices(
    origin: str,
    destination: str,
    departure_date: str,       # YYYY-MM-DD or YYYY-MM
    return_date: str = "",     # YYYY-MM-DD or YYYY-MM (empty = one-way)
    return_origin: str = "",   # IATA code for return departure (empty = same as destination)
    currency: str = "INR",
    limit: int = 10
) -> dict:
    """
    Fetch flight prices from Travelpayouts API.
    
    Supports:
    - Round trip (same city): single API call with one_way=false
    - Open-jaw (different return city): two one-way API calls combined
    - One-way fallback: if no return_date provided
    
    Returns:
        dict with 'outbound', 'return', and 'total_price' keys.
    """
    # Determine if this is an open-jaw route
    effective_return_origin = return_origin or destination
    is_open_jaw = effective_return_origin != destination
    
    print(f"\n{'='*60}")
    print(f"[FLIGHT SEARCH] {origin} → {destination}")
    print(f"  departure: {departure_date} | return: {return_date or 'NONE'}")
    print(f"  return_origin: {effective_return_origin} | open_jaw: {is_open_jaw}")
    print(f"  mode: {'ROUND TRIP' if return_date and not is_open_jaw else 'OPEN-JAW' if return_date and is_open_jaw else 'ONE-WAY'}")
    print(f"{'='*60}")
    
    if return_date and not is_open_jaw:
        # ── Standard round trip: single API call ──
        return await _fetch_round_trip(origin, destination, departure_date, return_date, currency, limit)
    elif return_date and is_open_jaw:
        # ── Open-jaw: two one-way calls ──
        return await _fetch_open_jaw(origin, destination, effective_return_origin, departure_date, return_date, currency, limit)
    else:
        # ── One-way fallback ──
        outbound = await _fetch_one_way(origin, destination, departure_date, currency, limit)
        return {
            "outbound": outbound,
            "return": [],
            "total_price": outbound[0]["price"] if outbound else None,
            "is_round_trip": False,
            "is_open_jaw": False
        }


async def _fetch_round_trip(
    origin: str, destination: str,
    departure_date: str, return_date: str,
    currency: str, limit: int
) -> dict:
    """Single API call for same-city round trip."""
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_date,
        "return_at": return_date,
        "one_way": "false",
        "direct": "false",
        "currency": currency,
        "limit": limit,
        "sorting": "price",
        "token": settings.TRAVELPAYOUTS_TOKEN
    }
    
    data = await _api_call(params)
    
    results = []
    for item in data:
        results.append(_parse_flight(item))
    
    return {
        "outbound": results,
        "return": [],  # Round-trip price is combined in the API response
        "total_price": results[0]["price"] if results else None,
        "is_round_trip": True,
        "is_open_jaw": False
    }


async def _fetch_open_jaw(
    origin: str, destination: str, return_origin: str,
    departure_date: str, return_date: str,
    currency: str, limit: int
) -> dict:
    """Two one-way calls for open-jaw trips (different return airport)."""
    # Outbound: origin → destination
    outbound = await _fetch_one_way(origin, destination, departure_date, currency, limit)
    # Return: return_origin → origin (fly back home from a different city)
    return_flights = await _fetch_one_way(return_origin, origin, return_date, currency, limit)
    
    # Fallback: if open-jaw return has no data, try returning from the destination airport instead
    actual_return_origin = return_origin
    if not return_flights and return_origin != destination:
        print(f"  [FALLBACK] No data for {return_origin} → {origin}, trying {destination} → {origin}")
        return_flights = await _fetch_one_way(destination, origin, return_date, currency, limit)
        actual_return_origin = destination
    
    # Fallback 2: if still no return data, try a standard round trip
    if not return_flights:
        print(f"  [FALLBACK] No return data at all, trying standard round trip")
        return await _fetch_round_trip(origin, destination, departure_date, return_date, currency, limit)
    
    # Calculate combined price from cheapest of each leg
    outbound_price = outbound[0]["price"] if outbound else 0
    return_price = return_flights[0]["price"] if return_flights else 0
    total = (outbound_price + return_price) if (outbound and return_flights) else None
    
    return {
        "outbound": outbound,
        "return": return_flights,
        "total_price": total,
        "is_round_trip": True,
        "is_open_jaw": actual_return_origin != destination,
        "open_jaw_info": {
            "outbound_route": f"{origin} → {destination}",
            "return_route": f"{actual_return_origin} → {origin}"
        }
    }


async def _fetch_one_way(
    origin: str, destination: str,
    departure_date: str, currency: str, limit: int
) -> List[dict]:
    """Single one-way API call."""
    params = {
        "origin": origin,
        "destination": destination,
        "departure_at": departure_date,
        "one_way": "true",
        "direct": "false",
        "currency": currency,
        "limit": limit,
        "sorting": "price",
        "token": settings.TRAVELPAYOUTS_TOKEN
    }
    
    data = await _api_call(params)
    return [_parse_flight(item) for item in data]


async def _api_call(params: dict) -> list:
    """Make the actual HTTP call to Travelpayouts."""
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"
    headers = {"Accept-Encoding": "gzip"}
    
    async with httpx.AsyncClient() as client:
        try:
            # Log the params being sent (hide token)
            log_params = {k: v for k, v in params.items() if k != 'token'}
            print(f"  [API CALL] params: {log_params}")
            
            response = await client.get(url, params=params, headers=headers, timeout=10.0)
            response.raise_for_status()
            data = response.json()
            
            print(f"  [API RESPONSE] success: {data.get('success')} | results: {len(data.get('data', []))}")
            for item in data.get('data', [])[:3]:
                print(f"    price: {item.get('price')} {params.get('currency','INR')} | airline: {item.get('airline')} | transfers: {item.get('transfers')} | return_at: {item.get('return_at', 'NONE')}")
            
            if not data.get("success"):
                return []
            
            return data.get("data", [])
        except Exception as e:
            print(f"Error fetching flight prices: {e}")
            return []


def _parse_flight(item: dict) -> dict:
    """Parse a single flight item from the API response."""
    return {
        "price": item.get("price"),
        "airline": item.get("airline"),
        "departure": item.get("departure_at"),
        "return_date": item.get("return_at", ""),
        "transfers": item.get("transfers"),
        "duration": item.get("duration"),
        "link": f"https://www.aviasales.com{item.get('link', '')}"
    }
