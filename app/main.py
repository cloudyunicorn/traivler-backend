from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import json
from app.graph import app_graph
from app.schemas.travel import TravelRequest

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def read_root():
    return {"status": "running"}


@app.post("/plan-trip")
async def plan_trip(req: TravelRequest):
    result = await app_graph.ainvoke({
        "user_input": req.model_dump()
    })

    return result["final_plan"]


@app.post("/stream-plan")
async def stream_plan(req: TravelRequest):
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