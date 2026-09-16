# CATALYST RISK - Interview Guide

This document prepares the candidate to present the CATALYST RISK platform effectively.

## Core Interview Talking Points

### 1. Vectorized Monte Carlo Simulation
**Question**: How does your model run 10,000 simulations across 500 properties so quickly?
**Answer**: "I specifically avoided native Python loops for the stochastic generation. Instead, the core `simulation.py` engine leverages numpy matrix broadcasting. I generate an array of event intensities, cross it with the local exposure variations to create an $N \times M$ intensity tensor, and map that through the logistic vulnerability function all in C-level memory space."

### 2. Separation of Concerns
**Question**: Why did you separate the mathematical engine from the Streamlit UI?
**Answer**: "To mimic production-level architecture. `app.py` strictly handles routing and UI state, while the core business logic (hazard, vulnerability, loss) resides in decoupled `src/` modules. This ensures the engine could theoretically be wrapped in a FastAPI REST layer later without refactoring the mathematics."

### 3. Model Validation
**Question**: How do you ensure the math is right?
**Answer**: "I built deterministic validation steps. The `validation.py` module mathematically guarantees that `Net Loss <= Ground-Up Loss` and `Net Loss <= Policy Limit`. If the stochastic sampling ever violates fundamental financial bounds, the engine deliberately crashes and logs the anomaly."

## "Demo Mode" Script
1. Open **Risk Simulation**.
2. Run standard baseline (10,000 simulations). Note the sub-second execution time.
3. Show **Overview Dashboard** (AAL, PML).
4. Go to **Sensitivity Analysis** and run the parameter sweep to show the dynamic engine recalculating outputs live based on shifting vulnerability and financial limits.
