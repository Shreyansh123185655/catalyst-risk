# CATALYST RISK - Methodology

## 1. Hazard
Hazard intensity represents the physical footprint of the natural catastrophe (e.g., wind speed for Windstorm, flood depth for Flood). In this prototype, intensity is sampled from a stochastic log-normal distribution.
$$ \mu = \ln(I_{base}) - \frac{\sigma^2}{2} $$
where $I_{base}$ is calibrated by the user-selected Hazard Type and Severity.

## 2. Vulnerability
Physical damage response is modeled using a standard Bounded Logistic function parameterized by construction material (Concrete, Steel, Wood, Masonry).
$$ DR = \frac{C_{cap}}{1 + e^{-k(I - I_{mid})}} $$
Where $C_{cap}$ represents the maximum possible damage percentage for the asset class.

## 3. Financial Loss
*   **Ground-Up Loss (GUL)** = $TIV \times DR$
*   **Net Insured Loss** = $\min(\max(GUL - Deductible, 0), Limit)$

## 4. Probabilistic Metrics
*   **Average Annual Loss (AAL)**: The statistical mean of simulated losses. Represents the baseline expected burn rate of the portfolio.
*   **Probable Maximum Loss (PML)**: Estimated tail risk. The $N$-year return period loss corresponds to the $(1 - 1/N)$ percentile of the aggregated annual loss distribution.
