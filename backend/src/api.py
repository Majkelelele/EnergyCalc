from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
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

class CSVFileNameRequest(BaseModel):
    date: str

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
    
@app.post("/api/process-csv")
def process_csv(request: CSVFileNameRequest):
    file_path =  "../data_months/tge/" + request.date + ".csv"

    # Read the CSV file
    try:
        data = pd.read_csv(file_path)

        # Ensure the CSV contains the required 'Data' column
        if 'Data' not in data.columns:
            raise HTTPException(status_code=400, detail="'Data' column missing in CSV")

        # Convert the 'Data' column to a list for processing
        data_list = data['Data'].tolist()

        # Process the data as needed (for demonstration, just return it)
        return {
            "data": data_list
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Run with: uvicorn api:app --reload
