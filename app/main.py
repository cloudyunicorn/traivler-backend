from fastapi import FastAPI
from app.graph import app_graph
from app.schemas.travel import TravelRequest

app = FastAPI()

@app.get("/")
def read_root():
    return {"status": "running"}


@app.post("/plan-trip")
async def plan_trip(req: TravelRequest):
    result = await app_graph.ainvoke({
        "user_input": req.model_dump()
    })

    return result["final_plan"]