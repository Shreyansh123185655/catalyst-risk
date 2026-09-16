import pandas as pd

def create_map_dataframe(exposure_df: pd.DataFrame, results: dict = None) -> pd.DataFrame:
    """
    Prepares a Geo-ready dataframe for Plotly rendering.
    We return a normal pandas dataframe formatted for Plotly Express Mapbox/Scattergeo.
    While GeoPandas can be used for deep spatial intersections in production,
    this module provides lightweight mapping integration for the prototype.
    """
    df = exposure_df.copy()
    
    # If results are provided, merge the expected losses
    if results is not None:
        property_mean_loss = results.get("property_mean_loss")
        if property_mean_loss is not None:
            df["expected_loss"] = property_mean_loss
            df["loss_ratio"] = property_mean_loss / df["tiv"]
            
            # Create a categorical risk band for visualization
            conditions = [
                (df['loss_ratio'] < 0.01),
                (df['loss_ratio'] >= 0.01) & (df['loss_ratio'] < 0.03),
                (df['loss_ratio'] >= 0.03)
            ]
            choices = ['Low', 'Elevated', 'High']
            import numpy as np
            df['risk_level'] = np.select(conditions, choices, default='Unknown')
    else:
        df["expected_loss"] = 0.0
        df["loss_ratio"] = 0.0
        df['risk_level'] = 'Low'
        
    return df
