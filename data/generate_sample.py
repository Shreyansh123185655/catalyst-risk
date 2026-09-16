import os
import pandas as pd
import numpy as np

def generate_synthetic_exposure(output_path="data/sample_exposure.csv", size=5000, seed=42):
    """
    Generates a deeply realistic synthetic dataset of properties representing a complex portfolio.
    Locations are clustered around multiple high-risk catastrophe zones.
    """
    np.random.seed(seed)
    
    # Major catastrophic hubs
    hubs = [
        {"name": "Miami (Hurricane)", "lat": 25.7617, "lon": -80.1918, "spread": 0.8, "hazard": "windstorm"},
        {"name": "Los Angeles (Quake)", "lat": 34.0522, "lon": -118.2437, "spread": 1.2, "hazard": "earthquake"},
        {"name": "Houston (Flood/Wind)", "lat": 29.7604, "lon": -95.3698, "spread": 1.0, "hazard": "flood"}
    ]
    
    b_types = ["Concrete", "Wood", "Steel", "Masonry"]
    
    data = []
    for i in range(size):
        hub = np.random.choice(hubs)
        lat = hub["lat"] + np.random.normal(0, hub["spread"])
        lon = hub["lon"] + np.random.normal(0, hub["spread"])
        
        # Real-world building distribution (Wood is common for residential)
        b_type = np.random.choice(b_types, p=[0.25, 0.60, 0.05, 0.10])
        
        # Log-normal distribution for property values (few very high value, many average)
        base_val = np.random.lognormal(mean=12.5, sigma=1.0) 
        
        # Ensure minimum value
        base_val = max(base_val, 50000.0)
        
        # Deductibles generally 2%, 5%, or 10% of TIV
        deductible = base_val * np.random.choice([0.02, 0.05, 0.10])
        
        # Policy limits often cap out or match TIV
        limit = base_val * np.random.choice([0.8, 1.0, 1.0, 1.0, 1.2])
        
        data.append({
            "location_id": f"LOC-{str(i+1).zfill(5)}",
            "region": hub["name"],
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "building_type": b_type,
            "tiv": round(base_val, 2),
            "deductible": round(deductible, 2),
            "policy_limit": round(limit, 2)
        })
        
    df = pd.DataFrame(data)
    
    # Ensure data directory exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    df.to_csv(output_path, index=False)
    print(f"Generated {size} deeply realistic synthetic records at {output_path}")
    return df

if __name__ == "__main__":
    generate_synthetic_exposure("data/sample_exposure.csv")
