import pandas as pd
import numpy as np

def load_exposure_data(file_path_or_buffer) -> pd.DataFrame:
    """
    Loads and validates exposure data from a CSV file or buffer.
    Ensures required columns exist and data types are correct.
    """
    df = pd.read_csv(file_path_or_buffer)
    
    required_cols = ['location_id', 'latitude', 'longitude', 'building_type', 'tiv']
    missing = [col for col in required_cols if col not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")
        
    # Validation checks
    if (df['tiv'] < 0).any():
        raise ValueError("Total Insured Value (TIV) cannot be negative.")
        
    if df['location_id'].duplicated().any():
        raise ValueError("Duplicate location_ids found in exposure data.")
        
    valid_coords = df['latitude'].between(-90, 90) & df['longitude'].between(-180, 180)
    if not valid_coords.all():
        raise ValueError("Invalid coordinates detected.")
        
    # Optional columns defaults
    if 'deductible' not in df.columns:
        df['deductible'] = 0.0
    if 'policy_limit' not in df.columns:
        df['policy_limit'] = np.inf
        
    return df

def get_exposure_summary(df: pd.DataFrame) -> dict:
    """Returns summary statistics for the exposure portfolio."""
    return {
        "total_properties": len(df),
        "total_tiv": df['tiv'].sum(),
        "average_tiv": df['tiv'].mean(),
        "max_tiv": df['tiv'].max(),
        "building_types": df['building_type'].value_counts().to_dict()
    }
