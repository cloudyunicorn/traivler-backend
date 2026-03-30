import requests
import json

API_TOKEN = "77edc470454f0908b5403beb879e3068"  # 🔴 replace

def test_flights():
    url = "https://api.travelpayouts.com/aviasales/v3/prices_for_dates"

    params = {
        "origin": "DEL",              # Delhi (IATA)
        "destination": "BKK",         # Bangkok
        "departure_at": "2026-04",    # YYYY-MM (recommended)
        "one_way": "true",
        "direct": "false",
        "currency": "INR",            # ⚠️ docs use RUB by default
        "limit": 10,
        "page": 1,
        "sorting": "price",
        "token": API_TOKEN
    }

    headers = {
        "Accept-Encoding": "gzip"   # recommended in docs
    }

    response = requests.get(url, params=params, headers=headers)
    data = response.json()

    print("\n✅ FULL RESPONSE:\n")
    print(json.dumps(data, indent=2))

    print("\n✈️ PARSED RESULTS:\n")

    if data.get("success"):
        for item in data.get("data", []):
            print({
                "price": item.get("price"),
                "airline": item.get("airline"),
                "departure": item.get("departure_at"),
                "stops": item.get("transfers"),
                "duration": item.get("duration"),
                "link": "https://www.aviasales.com" + item.get("link", "")
            })
    else:
        print("❌ Error:", data.get("error"))


if __name__ == "__main__":
    test_flights()