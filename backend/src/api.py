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
    starting_tarrif: str = "G11"
    tariff: str = "G13"
    
class LoadingRequest(BaseModel):
    provider: str = "enea"
    load_to_sell: bool = True
    start_date: str
    end_date: str

class CSVFileNameRequest(BaseModel):
    date: str

@app.post("/api/calculate")
def api_call(request: EnergyRequest):
    batteries, avg_profits, expected_months_to_returns, expected_months_cycles = simulate(
        do_print=False, grant=request.grant_applicable, daily_usage=request.daily_usage,
        provider=request.provider, load_to_sell=request.load_to_sell, tariff=request.tariff, starting_tariff=request.starting_tarrif, solar_avaialable=False
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
    f_rce =  "../data_months/rce/" + request.date + ".csv"

    prices = np.array((pd.read_csv(f_price).values).flatten())

    # usage already in kWh
    usage = np.array((pd.read_csv(f_usage).values).flatten())
    sell_prices = np.array((pd.read_csv(f_rce).values).flatten())

    # Read the CSV file
    try:
        # for b in BATTERIES:
        # load_to_use - (96 array) when and how much loading only to use later
        # grid_time - (96 array) when and how much we use energy directly from grid - only usage
        # load_to_sell - (96 array) when and how much buying only to sell later
        # unload_to_sell - (96 array) when and how much selling 
        load_to_use, grid_time, load_to_sell, unload_to_sell, month_const_cost_1, prices = run_best_algos_one_day(prices, usage, sell_prices, BATTERIES[2], request.load_to_sell, request.provider)
            
        unload_to_use = usage - grid_time

        time = load_to_use.tolist()

        state_dict = {
            'unload': 0,
            'load': 1,
            'idle': 2,
        }

        battery_state = []

        for i in range(96):
            state = 0
            if (load_to_use[i] > 0 or load_to_sell[i] > 0):
                state = state_dict["load"]
            elif (unload_to_use[i] > 0 or unload_to_sell[i] > 0):
                state = state_dict["unload"]
            else:
                state = state_dict["idle"]
            battery_state.append(state)
        print(battery_state)
        
        return {
            "data": battery_state,
        }
    
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="File not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@app.post("/api/benchmark_algos_cost")
def benchmark_algos_cost(request: LoadingRequest):
    res_algos_list = []
    res_benchmark_list = []
    for single_date in pd.date_range(request.start_date, request.end_date, freq='D'):
        
        f_price =  "../data_months/tge/" + str(single_date.date()) + ".csv"
        f_usage =  "../data_months/usage/" + str(single_date.date()) + ".csv"
        f_rce =  "../data_months/rce/" + str(single_date.date()) + ".csv"
        f_solar =  "../data_months/solar_output/" + str(single_date.date()) + ".csv"
        print(f_solar)

        print(f_usage)
        # Read the CSV file
        try:
            # for b in BATTERIES:
            res_algos, res_benchmark, _, _ = calculate_one_day(f_price, f_usage, f_rce, f_solar, battery=BATTERIES[2], load_to_sell=request.load_to_sell,
                                                               provider=request.provider,tariff="G13",starting_tariff="G11")
            
            # TODO
            # if res_algos is negative it means that we acutally could earn money, not only save money,
            # to add is check how much in theory can be earned
            
            res_algos_list.append(res_algos)
            res_benchmark_list.append(res_benchmark)

        except FileNotFoundError:
            raise HTTPException(status_code=404, detail="File not found")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    return {
        "res_algos": res_algos_list,
        "res_benchmark": res_benchmark_list,
    }
    
    

# Run with: uvicorn api:app --reload
