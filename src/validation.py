import numpy as np
import pandas as pd

def validate_losses(gul_matrix: np.ndarray, net_matrix: np.ndarray, deductibles: np.ndarray, limits: np.ndarray) -> bool:
    """
    Sanity checks to ensure mathematical and financial principles hold true.
    Raises ValueError if assertions fail.
    """
    # 1. Losses cannot be negative
    if np.any(gul_matrix < 0) or np.any(net_matrix < 0):
        raise ValueError("Validation failed: Negative losses detected.")
        
    # 2. Net loss cannot exceed Ground-Up Loss (accounting for floating point errors)
    if np.any(net_matrix > gul_matrix + 1e-5):
        raise ValueError("Validation failed: Net loss exceeds Ground-Up loss.")
        
    # 3. Net loss cannot exceed Policy Limit
    # limits shape is (num_properties,) - broadcasts to (num_sims, num_properties)
    if np.any(net_matrix > limits + 1e-5):
        raise ValueError("Validation failed: Net loss exceeds Policy Limit.")
        
    return True

def run_diagnostic_checks(results: dict) -> list:
    """
    Returns a list of diagnostic checks for the UI to display on the Validation page.
    """
    total_tiv = results["total_tiv"]
    losses = results["portfolio_net_losses"]
    gul = results["portfolio_gul_losses"]
    
    checks = []
    
    # 1. Total simulated years matches
    checks.append({
        "metric": "Simulation Count matches Request",
        "passed": len(losses) == results["sims"],
        "detail": f"{len(losses)} == {results['sims']}"
    })
    
    # 2. Net <= GUL at portfolio level
    checks.append({
        "metric": "Portfolio Net <= Portfolio GUL",
        "passed": bool(np.all(losses <= gul + 1e-5)),
        "detail": "Strict bounds maintained"
    })
    
    # 3. No negative portfolio losses
    checks.append({
        "metric": "No negative portfolio losses",
        "passed": bool(np.all(losses >= 0)),
        "detail": f"Min loss: ${np.min(losses):,.0f}"
    })
    
    # 4. AAL <= TIV
    aal = np.mean(losses)
    checks.append({
        "metric": "AAL <= Portfolio TIV",
        "passed": bool(aal <= total_tiv),
        "detail": f"${aal:,.0f} <= ${total_tiv:,.0f}"
    })
    
    return checks
