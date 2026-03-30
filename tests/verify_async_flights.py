import asyncio
import os
from dotenv import load_dotenv

# Mock settings since we are running outside the full app context
load_dotenv()

async def test_flight_search():
    from app.tools.flight_search import fetch_flight_prices
    from app.agents.flight_agent import flight_agent
    
    print("--- Testing fetch_flight_prices Tool ---")
    prices = await fetch_flight_prices(origin="DEL", destination="BKK", departure_date="2026-04")
    print(f"Found {len(prices)} flights.")
    if prices:
        print(f"Sample flight: {prices[0]}")
    
    print("\n--- Testing flight_agent (Budget) ---")
    budget_result = await flight_agent(origin="DEL", destination="BKK", travelers=1, budget="cheap")
    print(f"Budget per person: {budget_result.get('per_person')}")
    if budget_result.get('selected_option'):
        print(f"Selected: {budget_result['selected_option']['airline']} - {budget_result['selected_option']['price']}")

    print("\n--- Testing flight_agent (Luxury) ---")
    luxury_result = await flight_agent(origin="DEL", destination="BKK", travelers=1, budget="luxury")
    print(f"Luxury per person: {luxury_result.get('per_person')}")
    if luxury_result.get('selected_option'):
        print(f"Selected: {luxury_result['selected_option']['airline']} - {luxury_result['selected_option']['price']}")

if __name__ == "__main__":
    asyncio.run(test_flight_search())
