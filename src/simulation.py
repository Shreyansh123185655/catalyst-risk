import numpy as np
import pandas as pd
import time
from src.hazard import generate_hazard_events
from src.vulnerability import calculate_damage_ratio
from src.loss import calculate_ground_up_loss, calculate_net_loss
from src.validation import validate_losses

def run_monte_carlo_simulation(
    exposure_df: pd.DataFrame, 
    num_sims: int, 
    hazard_type: str, 
    severity: str, 
    event_freq: float,
    seed: int,
    vuln_shift: float = 1.0,
    deductible_shift: float = 1.0,
    limit_shift: float = 1.0
) -> dict:
    """
    Core vectorised Monte Carlo simulation engine.
    Avoids Python loops by executing matrix operations.
    """
    start_time = time.time()
    
    # 1. Generate stochastic hazard events
    events_df = generate_hazard_events(num_sims, hazard_type, severity, seed)
    event_intensities = events_df['intensity'].values
    
    # Probabilistic frequency filter (zeros out intensity if event doesn't occur that year)
    np.random.seed(seed + 1)
    event_occurs = np.random.rand(num_sims) < event_freq
    event_intensities = event_intensities * event_occurs
    
    num_properties = len(exposure_df)
    
    # 2. Extract exposure arrays
    tivs = exposure_df['tiv'].values
    b_types = exposure_df['building_type'].values
    
    # Apply sensitivity shifts to financial structures
    deductibles = exposure_df['deductible'].values * deductible_shift
    limits = exposure_df['policy_limit'].values * limit_shift
    
    # 3. Spatial / Local scaling approximation
    # In a real model, this would use exact GIS intersections. For performance,
    # we simulate local intensity variation with a random normal multiplier.
    np.random.seed(seed + 2)
    local_variation = np.random.normal(loc=1.0, scale=0.1, size=num_properties)
    local_variation = np.clip(local_variation, 0.7, 1.3)
    
    # Shape: (num_sims, num_properties)
    # Using outer product: intensity_matrix[i, j] = event_intensities[i] * local_variation[j]
    intensity_matrix = np.outer(event_intensities, local_variation)
    
    # 4. Calculate Damage Ratios and Losses
    # We loop over unique building types to vectorize over properties of that type
    damage_ratio_matrix = np.zeros_like(intensity_matrix)
    
    for b_type in np.unique(b_types):
        mask = (b_types == b_type)
        if mask.any():
            dr = calculate_damage_ratio(intensity_matrix[:, mask], b_type, vuln_shift)
            damage_ratio_matrix[:, mask] = dr
            
    # 5. Calculate Financials
    # tivs shape (num_properties,), broad-casted over (num_sims, num_properties)
    gul_matrix = calculate_ground_up_loss(tivs, damage_ratio_matrix)
    net_matrix = calculate_net_loss(gul_matrix, deductibles, limits)
    
    # 6. Validation bounds check
    validate_losses(gul_matrix, net_matrix, deductibles, limits)
    
    # 7. Aggregations
    portfolio_gul = np.sum(gul_matrix, axis=1)
    portfolio_net = np.sum(net_matrix, axis=1)
    property_mean_loss = np.mean(net_matrix, axis=0)
    
    # To save memory, we don't return the full N x M matrices, just the aggregated metrics
    results = {
        "run_id": f"CR-{int(time.time())}-{seed}",
        "sims": num_sims,
        "runtime_sec": round(time.time() - start_time, 4),
        "portfolio_net_losses": portfolio_net,
        "portfolio_gul_losses": portfolio_gul,
        "event_intensities": event_intensities,
        "property_mean_loss": property_mean_loss,
        "total_tiv": tivs.sum()
    }
    
    return results
