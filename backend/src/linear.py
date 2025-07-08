from __future__ import annotations
from typing import Tuple

import numpy as np
import pandas as pd
import pyomo.environ as pyo
# pyright: reportAttributeAccessIssue=false


def optimise_battery(
    prices: np.ndarray,
    demand: np.ndarray,
    Δ: float = 0.25,                 # h – length of one time-step
    C: float = 5.0,                  # kWh – battery capacity
    P_ch: float = 4.0,               # kW  – charge power limit
    P_dis: float = 4.0,              # kW  – discharge power limit
    eta_ch: float = 1.0,             # (–) charge efficiency
    eta_dis: float = 1.0,            # (–) discharge efficiency
    SOC0: float = 0.0,               # kWh – initial state of charge
    solver: str = "cbc",             # any Pyomo-compatible LP/MILP solver
    c_batt: float = 0.0,        # ← NEW: battery-throughput cost (€/kWh charged)

) -> Tuple[pd.DataFrame, float]:
    """
    Optimise battery dispatch; demand must be met by grid import + discharge.
    Returns a schedule DataFrame and the total grid-energy cost (€).
    """
    if prices.shape != demand.shape:
        raise ValueError("`prices` and `demand` must have the same length")

    # ---- PYOMO BUILD ------------------------------------------------------------
    T = range(len(prices))
    m = pyo.ConcreteModel()
    m.T = pyo.Set(initialize=T)

    # parameters
    m.price  = pyo.Param(m.T, initialize={t: float(prices[t])  for t in T})
    m.demand = pyo.Param(m.T, initialize={t: float(demand[t])  for t in T})

    # decision variables
    m.ch   = pyo.Var(m.T, bounds=(0, P_ch  * Δ))           # energy charged  (kWh)
    m.dis  = pyo.Var(m.T, bounds=(0, P_dis * Δ))           # energy discharged
    m.grid = pyo.Var(m.T, within=pyo.NonNegativeReals)     # grid import
    m.soc  = pyo.Var(range(len(prices) + 1), bounds=(0, C))
    m.mode = pyo.Var(m.T, within=pyo.Binary)               # 1 → charging mode

    m.soc[0].fix(SOC0)

    # battery dynamics
    def soc_rule(mm, t):
        return mm.soc[t+1] == mm.soc[t] + eta_ch * mm.ch[t] - mm.dis[t] / eta_dis
    m.soc_con = pyo.Constraint(m.T, rule=soc_rule)

    # demand must be covered by grid + discharge only
    def bal_rule(mm, t):
        return mm.grid[t] + mm.dis[t] == mm.demand[t]
    m.bal_con = pyo.Constraint(m.T, rule=bal_rule)

    # no simultaneous charge & discharge (big-M)
    def ch_limit(mm, t):
        return mm.ch[t] <= P_ch * Δ * mm.mode[t]
    def dis_limit(mm, t):
        return mm.dis[t] <= P_dis * Δ * (1 - mm.mode[t])
    m.ch_lim  = pyo.Constraint(m.T, rule=ch_limit)
    m.dis_lim = pyo.Constraint(m.T, rule=dis_limit)

    # finish with at least the initial SOC
    m.final_soc = pyo.Constraint(expr=m.soc[len(prices)] == SOC0)

    # objective: pay for every imported kWh (demand-side + battery charging)
    m.obj = pyo.Objective(
        expr=sum(
            m.price[t] * (m.grid[t] + m.ch[t])   # pay normal tariff on all imports
            + c_batt      *  m.ch[t]             # EXTRA € for each kWh into battery
            for t in m.T
        ),
        sense=pyo.minimize,
    )


    # ── Solve ───────────────────────────────────────────────────────────────
    pyo.SolverFactory(solver).solve(m, tee=False)

    # ── Results ─────────────────────────────────────────────────────────────
    schedule = pd.DataFrame({
        "price":      prices,
        "demand":     demand,
        "charge":     [pyo.value(m.ch[t])    for t in m.T],
        "discharge":  [pyo.value(m.dis[t])   for t in m.T],
        "grid_buy":   [pyo.value(m.grid[t])  for t in m.T],
        "soc":        [pyo.value(m.soc[t+1]) for t in m.T],
    })
    return schedule, float(pyo.value(m.obj))
