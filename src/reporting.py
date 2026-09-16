import pandas as pd
import json
import base64
from io import BytesIO

def create_export_csv(df: pd.DataFrame) -> bytes:
    """Converts DataFrame to CSV bytes for download."""
    return df.to_csv(index=False).encode('utf-8')

def generate_audit_trail(config: dict, results: dict) -> str:
    """
    Creates a JSON string combining the simulation configuration and summary results,
    providing a traceable audit trail for a specific run.
    """
    audit_data = {
        "run_id": results.get("run_id"),
        "timestamp": results.get("run_id", "").split("-")[1] if "-" in results.get("run_id", "") else "",
        "configuration": config,
        "summary_metrics": {
            "simulations": results.get("sims"),
            "runtime_sec": results.get("runtime_sec"),
            "total_tiv": results.get("total_tiv"),
        }
    }
    return json.dumps(audit_data, indent=2)

def generate_download_link(data: bytes, filename: str, mime_type: str = "text/csv") -> str:
    """
    Generates a raw HTML download link for a given byte string.
    Streamlit has st.download_button, but this is a utility if manual HTML links are needed.
    """
    b64 = base64.b64encode(data).decode()
    return f'<a href="data:{mime_type};base64,{b64}" download="{filename}">Download {filename}</a>'
