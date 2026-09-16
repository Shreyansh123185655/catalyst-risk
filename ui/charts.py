import plotly.graph_objects as go
import plotly.express as px
import pandas as pd

# Global Plotly Template for the Dark Premium Aesthetic
DARK_TEMPLATE = go.layout.Template(
    layout=go.Layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(color="#94A3B8", family="Inter, sans-serif", size=11),
        xaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.05)"),
        yaxis=dict(gridcolor="rgba(255,255,255,0.03)", zerolinecolor="rgba(255,255,255,0.05)"),
        colorway=["#38BDF8", "#818CF8", "#22C55E", "#F59E0B", "#EF4444"],
        hoverlabel=dict(
            bgcolor="rgba(17, 24, 39, 0.9)",
            font_size=12,
            font_family="IBM Plex Mono, monospace"
        ),
        margin=dict(l=40, r=20, t=40, b=30)
    )
)

def create_loss_distribution_chart(losses: list, aal: float, pml100: float, pml250: float):
    """Creates an interactive Plotly histogram of simulated losses with key markers."""
    fig = go.Figure()
    
    fig.add_trace(go.Histogram(
        x=losses,
        nbinsx=50,
        marker_color='#38BDF8',
        name="Scenarios",
        opacity=0.8
    ))
    
    # Add vertical lines for key metrics
    max_count = 1000 # arbitrary max for line height, plotly scales it
    
    fig.add_vline(x=aal, line_dash="dash", line_color="#22C55E", annotation_text="AAL", annotation_position="top right")
    fig.add_vline(x=pml100, line_dash="dash", line_color="#F59E0B", annotation_text="100Y PML", annotation_position="top right")
    fig.add_vline(x=pml250, line_dash="dash", line_color="#EF4444", annotation_text="250Y PML", annotation_position="top right")
    
    fig.update_layout(
        template=DARK_TEMPLATE,
        title="Annual Aggregate Loss Distribution",
        xaxis_title="Simulated Loss ($)",
        yaxis_title="Frequency",
        showlegend=False,
        bargap=0.05
    )
    return fig

def create_ep_curve(ep_df: pd.DataFrame, use_return_period: bool = True):
    """Creates the Exceedance Probability Curve."""
    fig = go.Figure()
    
    x_col = "return_period" if use_return_period else "probability"
    
    fig.add_trace(go.Scatter(
        x=ep_df[x_col],
        y=ep_df["loss"],
        mode='lines+markers',
        line=dict(color='#EF4444', width=2),
        marker=dict(size=6, color='#111827', line=dict(color='#EF4444', width=2)),
        name="OEP Curve"
    ))
    
    fig.update_layout(
        template=DARK_TEMPLATE,
        title="Exceedance Probability (EP) Curve",
        xaxis_title="Return Period (Years)" if use_return_period else "Annual Probability",
        yaxis_title="Loss Exceedance ($)",
        xaxis_type="log" if use_return_period else "linear"
    )
    
    if not use_return_period:
        fig.update_xaxes(autorange="reversed")
        
    return fig

def create_geo_map(df: pd.DataFrame, color_col: str = "expected_loss"):
    """Creates a Mapbox scatter map for exposure and risk visualization."""
    fig = px.scatter_mapbox(
        df, 
        lat="latitude", 
        lon="longitude", 
        color=color_col,
        size="tiv",
        hover_name="location_id",
        hover_data={"latitude": False, "longitude": False, "tiv": ":$,.0f", "expected_loss": ":$,.0f"},
        color_continuous_scale="Viridis" if color_col == "tiv" else "Inferno",
        zoom=9,
        center={"lat": df["latitude"].mean(), "lon": df["longitude"].mean()}
    )
    
    fig.update_layout(
        mapbox_style="carto-darkmatter",
        template=DARK_TEMPLATE,
        margin={"r":0,"t":0,"l":0,"b":0},
        coloraxis_colorbar=dict(title=color_col.replace("_", " ").title())
    )
    
    return fig
