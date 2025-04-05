from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
import pandas as pd
# from solar.solar_cell import SolarPanel
from calculator import simulate, run_best_algos_one_day, calculate_one_day
from backend.const import BATTERIES
import numpy as np

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
    
class LoadingRequest(BaseModel):
    provider: str = "enea"
    load_to_sell: bool = True
    date: str

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

@app.post("/api/grid_time-battery_time")
def process_csv(request: LoadingRequest):
    f_price =  "../data_months/tge/" + request.date + ".csv"
    f_usage =  "../data_months/usage/" + request.date + ".csv"
    prices = np.array((pd.read_csv(f_price).values).flatten())

    # usage already in kWh
    usage = np.array((pd.read_csv(f_usage).values).flatten())


    # Read the CSV file
    try:
        # for b in BATTERIES:
        battery_load_time, grid_time, buy, sell, month_const_cost_1, prices = run_best_algos_one_day(prices, usage, BATTERIES[2], request.load_to_sell, request.provider)
            

        battery_time = battery_load_time.tolist()
        grid_time = grid_time.tolist()
        return {
            "battery_time": battery_time,
            "grid_time": grid_time,
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/benchmark_algos_cost")
def process_csv(request: LoadingRequest):
    f_price =  "../data_months/tge/" + request.date + ".csv"
    f_usage =  "../data_months/usage/" + request.date + ".csv"


    # Read the CSV file
    try:
        # for b in BATTERIES:
        res_algos, res_benchmark, _, _ = calculate_one_day(f_price, f_usage, BATTERIES[0], request.load_to_sell, request.provider)        

        # TODO
        # if res_algos is negative it means that we acutally could earn money, not only save money,
        # to add is check how much in theory can be earned
        return {
            "res_algos": res_algos,
            "res_benchmark": res_benchmark,
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
    

# Run with: uvicorn api:app --reload
