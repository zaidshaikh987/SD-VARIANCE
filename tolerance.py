import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Configuration
st.set_page_config(
    page_title="⚙️ Engineering Tolerances Analyzer",
    layout="wide",
    page_icon="⚙️"
)

# Custom CSS
st.markdown("""
<style>
    [data-testid=stSidebar] {
        background: linear-gradient(0deg, #2C3E50 0%, #3498DB 100%);
        color: white;
    }
    .main .block-container {
        background: linear-gradient(180deg, #ffffff 0%, #f8f9fa 100%);
        padding: 2rem 2.5rem;
    }
    h1, h2, h3 {
        color: #2C3E50 !important;
        border-bottom: 2px solid #3498DB;
        padding-bottom: 0.3rem;
        text-shadow: 1px 1px 2px rgba(0,0,0,0.1);
    }
    .metric-box {
        padding: 1.5rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        background: white;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }
    .metric-box:hover {
        transform: translateY(-3px);
        box-shadow: 0 6px 12px rgba(0,0,0,0.15) !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Concepts & Controls
with st.sidebar:
    st.title("📘 Concepts & Controls")

    # Tolerance Parameters (Variance-Based)
    st.subheader("⚙️ Tolerance Parameters (Variance)")
    low_tolerance = st.slider("Low Variance Limit", 0.0000, 0.0100, 0.0004, 0.0001)
    high_tolerance = st.slider("High Variance Limit", 0.0000, 0.0200, 0.0016, 0.0001)

    # Educational Content
    st.subheader("📚 Key Concepts")
    st.markdown(f"""
    - **Tolerance**: The permissible limit or limits of variation in a physical dimension.
    - **Variance**: Measures how far a set of numbers are spread out from their average value.
    - **Risk Levels**:
        - 🔴 **High Risk**: Variance > {high_tolerance}
        - 🟡 **Medium Risk**: {low_tolerance} < Variance ≤ {high_tolerance}
        - 🟢 **Low Risk**: Variance ≤ {low_tolerance}
    """)

    # Real-World Example
    st.subheader("🛠️ Real-World Example")
    st.markdown("""
    A factory produces steel rods with a **target length of 100 mm**.
    
    - ✅ If **variance is small**, most rods fall within **±1 mm tolerance** (acceptable range).
    - ⚠️ If **variance increases**, more rods exceed the allowed limit, leading to:
        - **Rework**
        - **Scrap**
        - **Wasted resources**

    Keeping variance low ensures consistent quality and reduces production loss.
    """)

# Data Functions (Updated for Variance)
def calculate_variance(measurements):
    """Calculate variance for given measurements"""
    return np.var(measurements)

def risk_assessment(variance, low, high):
    """Determine risk category based on tolerance levels (variance-based)"""
    if variance > high:
        return '🔴 High Risk'
    elif variance > low:
        return '🟡 Medium Risk'
    return '🟢 Low Risk'

# Main App
st.title("⚙️ Engineering Tolerances Analyzer")
st.markdown("### Analyzing Part Measurements Based on Variance Tolerances")

# Input
col1, col2, col3 = st.columns([2, 1, 1])
with col1:
    measurements_input = st.text_area("Enter Measurements", help="Enter part measurements separated by commas (e.g., 10.02, 10.05, 10.03)")

# Process
if measurements_input:
    try:
        measurements = list(map(float, measurements_input.split(',')))
        if len(measurements) < 2:
            st.warning("Please provide at least two measurements.")
        else:
            variance = calculate_variance(measurements)
            risk_level = risk_assessment(variance, low_tolerance, high_tolerance)

            # Results
            st.markdown(f"### **Variance: {variance:.6f}**")
            st.markdown(f"### **Risk Level: {risk_level}**")

            fig = go.Figure()
            fig.add_trace(go.Histogram(x=measurements, nbinsx=10, name='Measurements'))
            fig.update_layout(title="Measurements Distribution",
                              xaxis_title="Measurement Value", 
                              yaxis_title="Frequency")
            st.plotly_chart(fig, use_container_width=True)

            st.markdown(f"""
            **Compliance Status:**
            - **Low Variance Limit**: {low_tolerance}
            - **High Variance Limit**: {high_tolerance}
            - Based on the variance, the part measurements are considered **{risk_level}**.
            """)
    except ValueError:
        st.error("Invalid input. Please ensure the measurements are numbers separated by commas.")
else:
    st.info("👈 Enter part measurements to begin variance analysis.")
