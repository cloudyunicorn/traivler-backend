from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from app.graph import app_graph
from app.schemas.travel import TravelRequest

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
                if node_name == "optimizer" and "final_plan" in state_update:
                    event_data["final_plan"] = state_update["final_plan"]
                
                yield f"data: {json.dumps(event_data)}\n\n"
        
        yield f"data: {json.dumps({'node': 'done', 'status': 'completed'})}\n\n"

    return StreamingResponse(event_generator(), media_type="text/event-stream")