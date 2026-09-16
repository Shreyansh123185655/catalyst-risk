import time
import os
import pandas as pd
import numpy as np
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import uvicorn

from src.simulation import run_monte_carlo_simulation
from src.metrics import calculate_aal, calculate_pml
from src.exposure import load_exposure_data

app = FastAPI(title="CATALYST RISK - Monte Carlo API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SimulationRequest(BaseModel):
    num_sims: int = 10000
    hazard_type: str = "windstorm"
    severity: str = "moderate"
    seed: int = 42
    deductible_shift: float = 1.0
    limit_shift: float = 1.0
    vuln_shift: float = 1.0
    event_freq: float = 0.20

def get_live_exposure():
    """Loads exposure data dynamically so changes to the CSV are reflected instantly."""
    try:
        return load_exposure_data("data/sample_exposure.csv")
    except Exception:
        return pd.DataFrame()

@app.get("/api/health")
def health_check():
    return {"status": "online", "version": "2.0.0"}

@app.get("/api/download/exposure")
def download_exposure():
    """Endpoint for the frontend to download the underlying portfolio data."""
    if not os.path.exists("data/sample_exposure.csv"):
        raise HTTPException(status_code=404, detail="File not found")
    return FileResponse("data/sample_exposure.csv", media_type="text/csv", filename="portfolio_exposure.csv")

@app.get("/api/exposure/summary")
def get_exposure_summary():
    df = get_live_exposure()
    if df.empty:
        raise HTTPException(status_code=404, detail="Exposure data not found.")
    
    tivs = df['tiv'].values
    return {
        "total_properties": len(df),
        "total_tiv": float(tivs.sum()),
        "max_tiv": float(tivs.max())
    }

@app.post("/api/simulate")
def simulate(req: SimulationRequest):
    df = get_live_exposure()
    if df.empty:
        raise HTTPException(status_code=500, detail="Exposure data not available on server.")
        
    start_api = time.time()
    
    res = run_monte_carlo_simulation(
        exposure_df=df,
        num_sims=req.num_sims,
        hazard_type=req.hazard_type,
        severity=req.severity,
        event_freq=req.event_freq,
        seed=req.seed,
        vuln_shift=req.vuln_shift,
        deductible_shift=req.deductible_shift,
        limit_shift=req.limit_shift
    )
    
    net_losses = res["portfolio_net_losses"]
    gross_losses = res["portfolio_gul_losses"]
    
    aal = calculate_aal(net_losses)
    sorted_losses = np.sort(net_losses)[::-1]
    pml100 = calculate_pml(sorted_losses, 100)
    pml250 = calculate_pml(sorted_losses, 250)
    
    payload = {
        "run_id": res["run_id"],
        "sims": req.num_sims,
        "hazType": req.hazard_type,
        "sevType": req.severity,
        "seed": req.seed,
        "totalTiv": float(res["total_tiv"]),
        "aal": float(aal),
        "pml100": float(pml100),
        "pml250": float(pml250),
        "losses": net_losses.tolist()[:25000], 
        "gross": gross_losses.tolist()[:25000],
        "avgPropLoss": res["property_mean_loss"].tolist(),
        "meanIntensity": float(np.mean(res["event_intensities"])),
        "execTime": res["runtime_sec"],
        "apiTime": round(time.time() - start_api, 4)
    }
    
    return payload

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
