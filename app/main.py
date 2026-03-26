from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
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