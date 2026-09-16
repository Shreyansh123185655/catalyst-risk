import streamlit as st
import pandas as pd
import numpy as np
import time

# Internal imports
from src.config import *
from src.exposure import load_exposure_data, get_exposure_summary
from src.simulation import run_monte_carlo_simulation
from src.metrics import calculate_aal, calculate_pml, generate_full_ep_curve, generate_ep_curve
from src.validation import run_diagnostic_checks
from src.geospatial import create_map_dataframe
from src.sensitivity import run_sensitivity_scenarios
from src.reporting import create_export_csv, generate_audit_trail
from ui.styles import apply_custom_css, render_top_header
from ui.charts import create_loss_distribution_chart, create_ep_curve, create_geo_map

st.set_page_config(page_title="CATALYST RISK", layout="wide", initial_sidebar_state="expanded")
apply_custom_css()

# Session State Initialization
if 'sim_results' not in st.session_state:
    st.session_state['sim_results'] = None
if 'exposure_df' not in st.session_state:
    st.session_state['exposure_df'] = None
if 'data_mode' not in st.session_state:
    st.session_state['data_mode'] = 'Synthetic Demo'

def load_data():
    if st.session_state['data_mode'] == 'Synthetic Demo':
        try:
            return load_exposure_data("data/sample_exposure.csv")
        except FileNotFoundError:
            st.error("Sample data not found. Please run `python data/generate_sample.py` first.")
            return None
    else:
        if st.session_state.get('uploaded_file') is not None:
            try:
                return load_exposure_data(st.session_state['uploaded_file'])
            except Exception as e:
                st.error(f"Error loading file: {e}")
                return None
        return None

# Sidebar Navigation
with st.sidebar:
    st.markdown('<div style="font-weight: 800; font-size: 16px; margin-bottom: 20px;"><span style="color: #38BDF8;">◈</span> CATALYST RISK</div>', unsafe_allow_html=True)
    
    page = st.radio("Navigation", [
        "Overview Dashboard",
        "Risk Simulation", 
        "Exposure Portfolio",
        "Geographic Risk",
        "EP Curve",
        "Sensitivity Analysis",
        "Model Validation"
    ], label_visibility="collapsed")
    
    st.markdown("---")
    st.markdown("### Data Source")
    new_data_mode = st.radio("Mode", ["Synthetic Demo", "Upload Exposure CSV"], label_visibility="collapsed")
    if new_data_mode != st.session_state['data_mode']:
        st.session_state['data_mode'] = new_data_mode
        st.session_state['exposure_df'] = None
        st.session_state['sim_results'] = None
        st.rerun()
        
    if st.session_state['data_mode'] == 'Upload Exposure CSV':
        uploaded_file = st.file_uploader("Upload CSV", type=['csv'])
        if uploaded_file:
            st.session_state['uploaded_file'] = uploaded_file
            st.session_state['exposure_df'] = None
            
    st.markdown("---")
    st.markdown("### System Status")
    if st.session_state['sim_results']:
        st.success("● Engine Ready")
    else:
        st.warning("● Waiting for Run")
    st.markdown("<div style='font-size:10px; color:#94a3b8;'>v1.0.0-STABLE</div>", unsafe_allow_html=True)

# Load data if not loaded
if st.session_state['exposure_df'] is None:
    df = load_data()
    if df is not None:
        st.session_state['exposure_df'] = df

exposure_df = st.session_state['exposure_df']

# Common Status for Header
status_dict = {
    "ready": st.session_state['sim_results'] is not None,
    "status_text": "MODEL READY" if st.session_state['sim_results'] else "PENDING SIMULATION",
    "events": st.session_state['sim_results']['sims'] if st.session_state['sim_results'] else 0,
    "runtime": st.session_state['sim_results']['runtime_sec'] if st.session_state['sim_results'] else 0.00
}

# --- PAGE: OVERVIEW DASHBOARD ---
if page == "Overview Dashboard":
    render_top_header("Portfolio Risk Overview", "A probabilistic view of catastrophe exposure, expected losses and extreme-event scenarios.", status_dict)
    
    if exposure_df is not None:
        if st.session_state['sim_results']:
            res = st.session_state['sim_results']
            aal = calculate_aal(res["portfolio_net_losses"])
            losses = np.sort(res["portfolio_net_losses"])[::-1]
            pml100 = calculate_pml(losses, 100)
            pml250 = calculate_pml(losses, 250)
            
            # KPIs
            c1, c2, c3, c4 = st.columns(4)
            c1.metric("Total Exposure", f"${res['total_tiv']:,.0f}", "Portfolio TIV")
            c2.metric("Expected Annual Loss", f"${aal:,.0f}", "AAL")
            c3.metric("100-Year PML", f"${pml100:,.0f}", "1.0% Annual Prob")
            c4.metric("250-Year PML", f"${pml250:,.0f}", "0.4% Annual Prob")
            
            st.markdown("### Risk Distribution")
            st.plotly_chart(create_loss_distribution_chart(res["portfolio_net_losses"], aal, pml100, pml250), use_container_width=True)
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("### Exceedance Probability")
                ep_df = generate_ep_curve(res["portfolio_net_losses"])
                st.plotly_chart(create_ep_curve(ep_df, use_return_period=True), use_container_width=True)
            
            with col2:
                st.markdown("### Portfolio Exposure")
                summary = get_exposure_summary(exposure_df)
                st.write(f"**Total Properties:** {summary['total_properties']:,}")
                st.write(f"**Average TIV:** ${summary['average_tiv']:,.0f}")
                st.write("**Building Types:**")
                st.json(summary['building_types'])
                
        else:
            st.info("Please navigate to 'Risk Simulation' and run the Monte Carlo engine to view results.")
    else:
        st.warning("Please load exposure data to begin.")

# --- PAGE: RISK SIMULATION ---
elif page == "Risk Simulation":
    render_top_header("Monte Carlo Risk Simulation", "Generate thousands of stochastic catastrophe scenarios to estimate the portfolio loss distribution.", status_dict)
    
    if exposure_df is not None:
        with st.form("sim_form"):
            col1, col2, col3 = st.columns(3)
            with col1:
                sims = st.selectbox("Number of Simulations", [1000, 5000, 10000, 20000, 50000], index=2)
                hazard_type = st.selectbox("Hazard Type", list(HAZARD_BASES.keys()))
                severity = st.selectbox("Hazard Severity", list(SEVERITY_MULTIPLIERS.keys()), index=1)
            with col2:
                seed = st.number_input("Random Seed", value=DEFAULT_SEED)
                freq = st.selectbox("Annual Event Rate", [0.05, 0.10, 0.20, 0.50], index=2)
                vuln_shift = st.slider("Vulnerability Curve Shift", 0.5, 1.5, 1.0, 0.05, help="1.0 is baseline. >1.0 increases damage.")
            with col3:
                ded_shift = st.slider("Portfolio Deductible Multiplier", 0.0, 2.0, 1.0, 0.1)
                lim_shift = st.slider("Portfolio Limit Multiplier", 0.5, 2.0, 1.0, 0.1)
                
            submitted = st.form_submit_button("▶ RUN SIMULATION")
            
        if submitted:
            with st.spinner("Executing stochastic risk engine..."):
                config = {
                    "num_sims": sims,
                    "hazard_type": hazard_type,
                    "severity": severity,
                    "event_freq": freq,
                    "seed": seed,
                    "vuln_shift": vuln_shift,
                    "deductible_shift": ded_shift,
                    "limit_shift": lim_shift
                }
                
                # Run the model
                results = run_monte_carlo_simulation(exposure_df, **config)
                st.session_state['sim_results'] = results
                st.session_state['last_config'] = config
                
                st.success(f"SIMULATION COMPLETE. Evaluated {sims:,} events in {results['runtime_sec']} seconds.")
                st.rerun()
                
        if st.session_state['sim_results']:
            st.markdown("### Latest Run Details")
            res = st.session_state['sim_results']
            st.write(f"**RUN ID:** `{res['run_id']}`")
            st.write(f"**Runtime:** {res['runtime_sec']} sec")
            
            # Model Audit Trail Export
            audit_json = generate_audit_trail(st.session_state['last_config'], res)
            st.download_button("Download Audit Trail (JSON)", audit_json, "audit_trail.json", "application/json")

# --- PAGE: EXPOSURE PORTFOLIO ---
elif page == "Exposure Portfolio":
    render_top_header("Exposure Portfolio", "Inspection of underlying physical assets and construction properties.", status_dict)
    if exposure_df is not None:
        st.dataframe(exposure_df.head(100), use_container_width=True)
        csv = create_export_csv(exposure_df)
        st.download_button("Download Full Exposure Data", csv, "exposure_data.csv", "text/csv")

# --- PAGE: GEOGRAPHIC RISK ---
elif page == "Geographic Risk":
    render_top_header("Geographic Risk", "Spatial distribution of the portfolio and localized risk metrics.", status_dict)
    if exposure_df is not None:
        map_df = create_map_dataframe(exposure_df, st.session_state['sim_results'])
        
        metric = st.radio("Map Layer", ["expected_loss", "tiv", "loss_ratio"], horizontal=True)
        
        st.plotly_chart(create_geo_map(map_df, metric), use_container_width=True)

# --- PAGE: EP CURVE ---
elif page == "EP Curve":
    render_top_header("Exceedance Probability Curve", "Return period analysis representing probability of exceeding loss thresholds.", status_dict)
    if st.session_state['sim_results']:
        losses = st.session_state['sim_results']['portfolio_net_losses']
        ep_dense = generate_full_ep_curve(losses)
        
        mode = st.radio("X-Axis", ["Return Period", "Probability"], horizontal=True)
        use_rp = mode == "Return Period"
        
        st.plotly_chart(create_ep_curve(ep_dense, use_rp), use_container_width=True)
        
        st.markdown("### Standard Return Periods")
        ep_summary = generate_ep_curve(losses)
        st.dataframe(ep_summary, use_container_width=True)

# --- PAGE: SENSITIVITY ANALYSIS ---
elif page == "Sensitivity Analysis":
    render_top_header("Sensitivity Analysis", "Impact of parameter uncertainty on expected portfolio losses.", status_dict)
    if st.session_state['sim_results'] and 'last_config' in st.session_state:
        if st.button("Run Parameter Sweep"):
            with st.spinner("Running multiple Monte Carlo configurations..."):
                sens_df = run_sensitivity_scenarios(exposure_df, st.session_state['last_config'])
                st.dataframe(sens_df, use_container_width=True)
                
                # Simple bar chart
                fig = px.bar(sens_df, x="Change (%)", y="Scenario", orientation='h', color="Change (%)", color_continuous_scale="RdYlGn_r")
                fig.update_layout(template=DARK_TEMPLATE)
                st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Run a baseline simulation first.")

# --- PAGE: MODEL VALIDATION ---
elif page == "Model Validation":
    render_top_header("Model Validation & Audit", "Sanity checks and financial reconciliation for the current simulation run.", status_dict)
    if st.session_state['sim_results']:
        checks = run_diagnostic_checks(st.session_state['sim_results'])
        for check in checks:
            status_icon = "✅ PASS" if check["passed"] else "❌ FAIL"
            st.markdown(f"**{status_icon} | {check['metric']}**")
            st.markdown(f"<div style='margin-left: 20px; font-family: monospace; color: #94A3B8;'>{check['detail']}</div>", unsafe_allow_html=True)
            st.markdown("---")
