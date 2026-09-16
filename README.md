# CATALYST RISK - Stochastic Catastrophe Risk Platform

CATALYST RISK is a high-performance, stochastic catastrophe risk modeling platform built in Python. Designed for quantitative risk analysts and reinsurance professionals, it allows users to run thousands of Monte Carlo simulations to estimate expected and tail financial losses across a geographically distributed property portfolio.

## Key Features
*   **Vectorized Monte Carlo Engine**: Simulate 10,000+ stochastic hazard scenarios across hundreds of properties in sub-second speeds using pure NumPy tensor operations.
*   **Premium Analytical UI**: A completely custom, dark-themed Streamlit frontend built to mimic tier-1 fintech interfaces (Palantir/Bloomberg).
*   **Mathematical Integrity**: Real-time calculation of Average Annual Loss (AAL), Probable Maximum Loss (PML), and Exceedance Probability (EP) curves based on explicit stochastic simulation, not hardcoded dashboard mockups.
*   **Sensitivity & Audit**: Built-in parameter sweep logic to test model sensitivity, complete with simulation run IDs, exact seeds, and downloadable diagnostic audit trails.

## Quick Start
1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Generate the synthetic demo dataset:
```bash
python data/generate_sample.py
```

3. Launch the application:
```bash
streamlit run app.py
```

## Project Architecture
*   `app.py`: Streamlit routing and UI state management.
*   `src/`: Modular backend risk engine (hazard, vulnerability, financial structures, vectorised monte-carlo).
*   `ui/`: Custom CSS injection and Plotly chart configurations.
*   `tests/`: Suite of unit tests ensuring mathematical rules are bounded correctly (e.g., Net Loss cannot exceed Limit).

Please review the `docs/` folder for deeper dives into the quantitative methodology and architecture.
