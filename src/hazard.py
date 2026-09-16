import numpy as np
import pandas as pd
from src.config import HAZARD_BASES, SEVERITY_MULTIPLIERS

def generate_hazard_events(num_events: int, hazard_type: str, severity: str, seed: int = 42) -> pd.DataFrame:
    """
    Generates stochastic hazard events.
    Uses log-normal distribution to represent natural catastrophe intensity.
    
    Returns: DataFrame with event_id and base_intensity.
    """
    np.random.seed(seed)
    
    if hazard_type not in HAZARD_BASES:
        raise ValueError(f"Unknown hazard type: {hazard_type}")
    if severity not in SEVERITY_MULTIPLIERS:
        raise ValueError(f"Unknown severity: {severity}")
        
    base_intensity = HAZARD_BASES[hazard_type] * SEVERITY_MULTIPLIERS[severity]
    
    # Stochastic sampling using log-normal distribution
    # We define mu and sigma such that the mean aligns roughly with base_intensity
    # For a log-normal, mean = exp(mu + sigma^2 / 2)
    sigma = 0.32
    mu = np.log(base_intensity) - (sigma**2 / 2)
    
    intensities = np.random.lognormal(mean=mu, sigma=sigma, size=num_events)
    
    events = pd.DataFrame({
        "event_id": [f"EVT-{str(i+1).zfill(5)}" for i in range(num_events)],
        "intensity": intensities
    })
    
    return events
