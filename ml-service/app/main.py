from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import numpy as np
from scipy.integrate import odeint

app = FastAPI(title="SymptoMap ML Service", version="1.0.0")

class SEIRParameters(BaseModel):
    population: int
    initial_infected: int
    initial_exposed: int = 0
    initial_recovered: int = 0
    beta: float  # Transmission rate
    sigma: float # Incubation rate (1/incubation_period)
    gamma: float # Recovery rate (1/infectious_period)
    days: int

class PredictionPoint(BaseModel):
    day: int
    susceptible: float
    exposed: float
    infected: float
    recovered: float

class SEIRResponse(BaseModel):
    predictions: List[PredictionPoint]
    peak_infected: float
    peak_day: int

@app.get("/")
async def root():
    return {"status": "online", "service": "SymptoMap ML Service"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

def seir_model(y, t, N, beta, sigma, gamma):
    S, E, I, R = y
    dSdt = -beta * S * I / N
    dEdt = beta * S * I / N - sigma * E
    dIdt = sigma * E - gamma * I
    dRdt = gamma * I
    return dSdt, dEdt, dIdt, dRdt

@app.post("/predict/seir", response_model=SEIRResponse)
async def predict_seir(params: SEIRParameters):
    try:
        N = params.population
        I0 = params.initial_infected
        E0 = params.initial_exposed
        R0 = params.initial_recovered
        S0 = N - I0 - E0 - R0
        
        # Time vector
        t = np.linspace(0, params.days, params.days + 1)
        
        # Initial conditions vector
        y0 = S0, E0, I0, R0
        
        # Integrate the SIR equations over the time grid, t.
        ret = odeint(seir_model, y0, t, args=(N, params.beta, params.sigma, params.gamma))
        S, E, I, R = ret.T
        
        predictions = []
        peak_infected = 0
        peak_day = 0
        
        for i in range(len(t)):
            predictions.append(PredictionPoint(
                day=int(t[i]),
                susceptible=float(S[i]),
                exposed=float(E[i]),
                infected=float(I[i]),
                recovered=float(R[i])
            ))
            
            if I[i] > peak_infected:
                peak_infected = float(I[i])
                peak_day = int(t[i])
                
        return SEIRResponse(
            predictions=predictions,
            peak_infected=peak_infected,
            peak_day=peak_day
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# Import spread predictor
from app.spread_predictor import SpreadPredictor, OutbreakLocation, SpreadPredictionResult

spread_predictor = SpreadPredictor()


class SpreadPredictionRequest(BaseModel):
    outbreaks: List[OutbreakLocation]
    bounds: dict  # {north, south, east, west}


@app.post("/predict/spread", response_model=SpreadPredictionResult)
async def predict_spread(request: SpreadPredictionRequest):
    """
    Predict geographic spread of disease from current outbreak locations
    
    Returns risk scores for surrounding areas, prioritized list of high-risk locations,
    and a heatmap grid for visualization.
    """
    try:
        result = spread_predictor.find_at_risk_areas(
            outbreaks=request.outbreaks,
            bounds=request.bounds
        )
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
