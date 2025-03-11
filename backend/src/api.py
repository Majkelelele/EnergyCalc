from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
# from solar.solar_cell import SolarPanel
from calculator import simulate

app = FastAPI()

# Allow frontend calls (adjust origins for production)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Use specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Define the request model
class EnergyRequest(BaseModel):
    daily_usage: float
    grant_applicable: bool = False
    provider: str = "enea"
    load_to_sell: bool = True

@app.post("/api/calculate")
def api_call(request: EnergyRequest):
    batteries, avg_profits, expected_months_to_returns, expected_months_cycles = simulate(
        do_print=False, grant=request.grant_applicable, daily_usage=request.daily_usage,
        provider=request.provider, load_to_sell=request.load_to_sell
    )

    return {
        "batteries": batteries,
        "avg_profits": avg_profits,
        "expected_months_to_returns": expected_months_to_returns,
        "expected_months_cycles": expected_months_cycles,
    }

# Run with: uvicorn api:app --reload
