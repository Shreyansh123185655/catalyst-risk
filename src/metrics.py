import numpy as np
import pandas as pd
from src.config import RETURN_PERIODS

def calculate_aal(losses: np.ndarray) -> float:
    """Calculates Average Annual Loss (AAL)."""
    return float(np.mean(losses))

def calculate_pml(sorted_desc_losses: np.ndarray, return_period: int) -> float:
    """
    Calculates the Probable Maximum Loss (PML) for a specific return period.
    Assumes annual occurrence logic (OEP / AEP approximation).
    """
    num_sims = len(sorted_desc_losses)
    # The return period dictates the probability threshold.
    # A 100-year return period means a 1/100 (1%) probability of exceedance.
    index = int(np.floor(num_sims / return_period)) - 1
    # clamp index between 0 and max length
    index = max(0, min(index, num_sims - 1))
    return float(sorted_desc_losses[index])

def generate_ep_curve(losses: np.ndarray) -> pd.DataFrame:
    """
    Generates Exceedance Probability (EP) curve data.
    """
    sorted_losses = np.sort(losses)[::-1]
    num_sims = len(sorted_losses)
    
    # Calculate EP for the required return periods
    ep_data = []
    for rp in RETURN_PERIODS:
        loss_val = calculate_pml(sorted_losses, rp)
        ep_data.append({
            "return_period": rp,
            "probability": 1.0 / rp,
            "loss": loss_val
        })
        
    return pd.DataFrame(ep_data)

def generate_full_ep_curve(losses: np.ndarray) -> pd.DataFrame:
    """
    Generates a dense EP curve for plotting.
    Filters to significant non-zero events for rendering efficiency.
    """
    sorted_losses = np.sort(losses)[::-1]
    sorted_losses = sorted_losses[sorted_losses > 0]
    num_events = len(sorted_losses)
    total_sims = len(losses)
    
    if num_events == 0:
        return pd.DataFrame({"loss": [0], "probability": [0], "return_period": [0]})
        
    # Take a subset of points (e.g., 200) to keep Plotly fast
    indices = np.linspace(0, num_events - 1, min(200, num_events), dtype=int)
    plot_losses = sorted_losses[indices]
    
    # Probability = Rank / Total Simulations
    ranks = indices + 1
    probabilities = ranks / total_sims
    return_periods = 1.0 / probabilities
    
    return pd.DataFrame({
        "loss": plot_losses,
        "probability": probabilities,
        "return_period": return_periods
    })
