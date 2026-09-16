import pandas as pd
from src.simulation import run_monte_carlo_simulation
from src.metrics import calculate_aal

def run_sensitivity_scenarios(exposure_df: pd.DataFrame, base_config: dict) -> pd.DataFrame:
    """
    Runs isolated parameter shifts to determine model sensitivity.
    Returns a DataFrame with scenario name, relative change, and absolute AAL.
    """
    
    # Run Baseline
    res_base = run_monte_carlo_simulation(exposure_df, **base_config)
    aal_base = calculate_aal(res_base["portfolio_net_losses"])
    
    scenarios = [
        {"name": "Baseline", "kwargs": {}},
        {"name": "+10% Hazard", "kwargs": {"hazard_type": base_config["hazard_type"], "severity": base_config["severity"]}}, # Simplified via a shift if we had one
        {"name": "+10% Vulnerability", "kwargs": {"vuln_shift": 1.10}},
        {"name": "-10% Deductible", "kwargs": {"deductible_shift": 0.90}},
        {"name": "+20% Policy Limit", "kwargs": {"limit_shift": 1.20}},
    ]
    
    # We will simulate the hazard shift mathematically for the prototype by shifting vulnerability equivalent
    # since hazard generation is stochastic and non-linear.
    scenarios[1]["kwargs"]["vuln_shift"] = 1.15 # rough proxy for hazard increase
    
    results = []
    
    for sc in scenarios:
        # Merge base config with scenario overrides
        config = base_config.copy()
        config.update(sc["kwargs"])
        
        # In a real model, we might want to avoid re-running random seeds entirely,
        # but for demonstration we run the full engine
        if sc["name"] == "Baseline":
            aal = aal_base
        else:
            res = run_monte_carlo_simulation(exposure_df, **config)
            aal = calculate_aal(res["portfolio_net_losses"])
            
        pct_change = ((aal - aal_base) / aal_base) * 100 if aal_base else 0.0
        
        results.append({
            "Scenario": sc["name"],
            "AAL ($)": aal,
            "Change (%)": pct_change
        })
        
    return pd.DataFrame(results)
