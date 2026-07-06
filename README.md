# ⚙️ Traivler Backend — Multi-Agent AI Travel Orchestrator

The backend of **Traivler** is a high-performance, asynchronous Python service built with **FastAPI** and orchestrated using **LangGraph**. It acts as a travel planning coordinator that runs parallel LLM agents and web searchers to output structured travel plans.

---

## 🏗️ Architecture & Agent Pipeline

The core intelligence of the backend is built on a directed acyclic graph (DAG) managed by **LangGraph** (defined in [app/graph.py](app/graph.py)). 

Here is the flow of the LangGraph node execution:

```
                  ┌───────────────┐
                  │    START      │
                  └───────┬───────┘
          ┌───────────────┼───────────────┐
          ▼               ▼               ▼
   ┌────────────┐  ┌────────────┐  ┌────────────┐
   │   search   │  │   flight   │  │   hotel    │
   │   node     │  │   node     │  │   node     │
   └──────┬─────┘  └──────┬─────┘  └──────┬─────┘
          │               │               │
          └───────────────┼───────────────┘
                          ▼
                  ┌───────────────┐
                  │   itinerary   │
                  │   node        │
                  └───────┬───────┘
                          ▼
                  ┌───────────────┐
                  │   optimizer   │
                  │   node        │
                  └───────┬───────┘
                          ▼
                  ┌───────────────┐
                  │     cost      │
                  │     node      │
                  └───────┬───────┘
                          ▼
                  ┌───────────────┐
                  │     END       │
                  └───────────────┘
```

### 🧠 The Agent Workflow

1. **START**: Receives the user's travel parameters from the frontend (represented by [TravelRequest](app/schemas/travel.py)).
2. **Parallel Fan-out**:
   - **Search Agent** ([search_agent.py](app/agents/search_agent.py)): Queries DuckDuckGo for top-rated attractions, activities, and local guides matching the user's destination, travel intent, and avoids constraints.
   - **Flight Node** ([graph.py](app/graph.py#L28)):
     - **Route Agent** ([route_agent.py](app/agents/route_agent.py)): Resolves the destination name to appropriate IATA codes and determines whether a standard round trip or an open-jaw (arriving in one airport, departing from another) route fits best.
     - **Flight Agent** ([flight_agent.py](app/agents/flight_agent.py)): Interacts with the Travelpayouts Flight API to retrieve real prices in the user's chosen currency, executing fallback logic if no exact results exist.
   - **Hotel Agent** ([hotel_agent.py](app/agents/hotel_agent.py)): Researches optimal neighborhoods and hotel rate guidelines based on dates, group size, travelers' composition (e.g., family/kids), and seasonality.
3. **Itinerary Agent** ([itinerary_agent.py](app/agents/itinerary_agent.py)): Consolidates recommendations from the search, flight, and hotel nodes. Generates a day-by-day timeline geographically clustered around hotel recommendations, ensuring logical transitions and matching the requested trip pace and traveler fitness levels.
4. **Optimizer Agent** ([optimizer.py](app/agents/optimizer.py)): Structures the raw text from the previous agents into a strict, type-safe JSON structure matching the [TravelResponse](app/schemas/travel.py#L65) schema.
5. **Cost Verification Agent** ([cost_agent.py](app/agents/cost_agent.py)): A validator agent that performs concurrent web searches for average local prices of meals, local transport, and attraction tickets. It recalculates the math for the entire trip to verify that the final cost breakdown is realistic, preventing LLM hallucinations.
6. **END**: Returns the validated, structured travel itinerary.

---

## ✈️ Flight Search Fallback Architecture

To guarantee the user always receives flights, the [flight_search.py](app/tools/flight_search.py) tool implements a fallback matrix:

- **Open-Jaw Routing**: If returning from a different airport (e.g. fly into Tokyo, leave from Osaka), it executes two distinct one-way API calls. If the Osaka flight is missing, it falls back to a return from Tokyo, and if that fails, it falls back to a standard round trip.
- **Date Generalization**: If exact dates yield no flights, the system falls back to querying the entire departure month. If that also fails, it searches the following month (beneficial for edge-of-month dates).
- **Search Engine Fallback**: If the Travelpayouts API returns no fares, the Flight Agent initiates a fallback search query via DuckDuckGo to extract typical airline prices for the route, ensuring the budget estimates are populated.

---

## 🛠️ Technology Stack

- **Framework**: [FastAPI](https://fastapi.tiangolo.com/) for fast, asynchronous API endpoints.
- **Orchestration**: [LangGraph](https://langchain-ai.github.io/langgraph/) to construct the multi-agent execution DAG.
- **AI Integrations**: [LangChain OpenAI](https://github.com/langchain-ai/langchain) to communicate with GPT models (`gpt-4o-mini` and `gpt-4o`).
- **External Queries**: `duckduckgo-search` for real-time web scraping.
- **Rate Limiting**: `slowapi` to protect routes against abuse.
- **Package Manager**: [uv](https://github.com/astral-sh/uv) for fast Python package resolution and environment management.

---

## ⚙️ Environment Variables & Config

Create a `.env` file in the backend root directory (configured via [app/config.py](app/config.py)):

```env
OPENAI_API_KEY="sk-proj-..."
MODEL_NAME="gpt-4o-mini"       # Model for standard tasks
MODEL_NAME2="gpt-4o"           # Model for cost verification and optimization
TEMPERATURE=0.3
DEBUG=True

# Travelpayouts / Aviasales API Token for real-time flight searches
TRAVELPAYOUTS_TOKEN="your_token_here"

# (Optional) LangSmith tracing configuration
LANGSMITH_TRACING=true
LANGSMITH_ENDPOINT="https://api.smith.langchain.com"
LANGSMITH_API_KEY="lsv2_pt_..."
LANGSMITH_PROJECT="traivler"
```

---

## 🚀 Getting Started

### 1. Installation
We recommend using the Astral `uv` tool for fast dependency installation.

```bash
# Clone the repository and navigate to the backend folder
cd traivler-backend

# Install dependencies and create a virtual environment
uv sync
```

### 2. Running Locally
Launch the API server with hot-reloading enabled:

```bash
uv run uvicorn app.main:app --reload
```

The server will spin up on [http://localhost:8000](http://localhost:8000). You can access the interactive Swagger documentation at [http://localhost:8000/docs](http://localhost:8000/docs).

---

## 📡 API Endpoints

### `GET /`
- **Description**: Health check endpoint.
- **Response**: `{"status": "running"}`

### `GET /airports/search?q={query}`
- **Description**: Autocomplete fuzzy search for airports and cities using the Aviasales Autocomplete API. Cached in-memory to prevent API exhaustion.
- **Response**: List of items containing airport name, city name, and IATA codes.

### `POST /plan-trip`
- **Description**: Synchronously runs the entire LangGraph pipeline. Blocks until completion.
- **Body**: [TravelRequest](app/schemas/travel.py)
- **Response**: Structured `TravelResponse` JSON.

### `POST /stream-plan`
- **Description**: Initiates the LangGraph pipeline and returns progress events using Server-Sent Events (SSE). Used by the frontend to render real-time pipeline status trackers.
- **Body**: [TravelRequest](app/schemas/travel.py)
- **Response stream data events**:
  - `{"node": "start", "status": "completed"}`
  - `{"node": "search", "status": "completed"}`
  - `{"node": "flight", "status": "completed"}`
  - `{"node": "hotel", "status": "completed"}`
  - `{"node": "itinerary", "status": "completed"}`
  - `{"node": "optimizer", "status": "completed"}`
  - `{"node": "cost", "status": "completed", "final_plan": { ... }}`
  - `{"node": "done", "status": "completed"}`
