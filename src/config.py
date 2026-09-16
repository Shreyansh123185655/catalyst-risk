"""
CATALYST RISK Platform - Global Configuration
This module stores default parameters, model configurations, and constants
used across the catastrophic risk engine.
"""

# Default Simulation Parameters
DEFAULT_SIMULATIONS = 10000
DEFAULT_SEED = 42
DEFAULT_HAZARD = "windstorm"
DEFAULT_SEVERITY = "moderate"
DEFAULT_DEDUCTIBLE = 25000.0
DEFAULT_LIMIT = 750000.0

# Hazard Configuration
HAZARD_BASES = {
    "windstorm": 100.0,
    "flood": 80.0,
    "earthquake": 120.0,
    "wildfire": 90.0
}

SEVERITY_MULTIPLIERS = {
    "low": 0.72,
    "moderate": 1.0,
    "high": 1.30,
    "extreme": 1.65
}

# Vulnerability Logistic Curve Parameters
# mid: intensity at which damage is half of cap
# k: steepness of the curve
# cap: maximum mean damage ratio
VULNERABILITY_PARAMS = {
    "Concrete": {"mid": 140.0, "k": 0.032, "cap": 0.85},
    "Wood": {"mid": 90.0, "k": 0.045, "cap": 0.97},
    "Steel": {"mid": 155.0, "k": 0.030, "cap": 0.70},
    "Masonry": {"mid": 105.0, "k": 0.038, "cap": 0.92}
}

# Return Periods for Reporting
RETURN_PERIODS = [250, 100, 50, 25, 10, 5, 2, 1]

# Demo Data Generation Parameters
DEMO_PORTFOLIO_SIZE = 500
DEMO_CENTER_LAT = 34.0522  # Los Angeles (Fictional Metro)
DEMO_CENTER_LON = -118.2437
DEMO_SPREAD = 0.5  # degrees

BUILDING_TYPES = ["Concrete", "Wood", "Steel", "Masonry"]
