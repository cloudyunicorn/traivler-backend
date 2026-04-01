from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.graph import app_graph
from app.schemas.travel import TravelRequest
from typing import Dict, List
import httpx

limiter = Limiter(key_func=get_remote_address)
app = FastAPI()

app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:8000", "https://traivler.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
@limiter.limit("20/minute")
def read_root(request: Request):
    return {"status": "running"}


@app.post("/plan-trip")
@limiter.limit("5/minute")
async def plan_trip(request: Request, req: TravelRequest):
    result = await app_graph.ainvoke({
        "user_input": req.model_dump()
    })

    return result["final_plan"]


@app.post("/stream-plan")
@limiter.limit("5/minute")
async def stream_plan(request: Request, req: TravelRequest):
    async def event_generator():
        yield f"data: {json.dumps({'node': 'start', 'status': 'completed'})}\n\n"
        
        async for output in app_graph.astream(
            {"user_input": req.model_dump()},
            stream_mode="updates"
        ):
            for node_name, state_update in output.items():
                event_data = {
                    "node": node_name,
                    "status": "completed"
                }
                if node_name == "cost" and "final_plan" in state_update:
                    event_data["final_plan"] = state_update["final_plan"]
                
                yield f"data: {json.dumps(event_data)}\n\n"
        
        yield f"data: {json.dumps({'node': 'done', 'status': 'completed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")


# Simple in-memory search cache (query -> results)
_search_cache: Dict[str, List[dict]] = {}


@app.get("/airports/search")
@limiter.limit("30/minute")
async def search_airports(request: Request, q: str = ""):
    """
    Search for airports using fuzzy matching.
    """
    query = q.strip().lower()
    
    # Check cache for exact match
    if query in _search_cache:
        return _search_cache[query]
    
    # Fetch from Aviasales API if query is at least 2 characters
    results = []
    if len(query) >= 2:
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    "https://autocomplete.travelpayouts.com/places2",
                    params={
                        "term": query,
                        "locale": "en",
                        "types[]": ["airport", "city", "country"],
                    },
                    timeout=5.0
                )
                
                if response.status_code == 200:
                    api_data = response.json()
                    for item in api_data:
                        results.append({
                            "name": item.get("name", ""),
                            "code": item.get("code", ""),
                            "type": item.get("type", "airport"),
                            "city_name": item.get("city_name", ""),
                            "country_name": item.get("country_name", ""),
                            "city_code": item.get("city_code", ""),
                            "country_code": item.get("country_code", "")
                        })
                        if len(results) >= 10:
                            break
        except Exception as e:
            print(f"Error fetching from Aviasales API: {e}")
            # we return empty list or cached results if any error occurs
            pass
    
    # Basic cache management (keep last 100 queries)
    if query and results:
        if len(_search_cache) > 100:
            # Clear cache if it gets too big (naive)
            _search_cache.clear()
        _search_cache[query] = results
        
    return results