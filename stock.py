import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import google.generativeai as genai
from datetime import datetime
from functools import lru_cache

# Configuration
st.set_page_config(
    page_title="📊 Stock Volatility Analyzer",
    layout="wide",
    page_icon="📈"
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
    .gemini-insight {
        background: #f0f4f8;
        border-left: 4px solid #3498DB;
        padding: 1.5rem;
        border-radius: 8px;
        margin: 1.5rem 0;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    [data-baseweb="tab-list"] {
        gap: 10px;
    }
    [data-baseweb="tab"] {
        background: #e8f4fc !important;
        border-radius: 8px !important;
        padding: 8px 20px !important;
        transition: all 0.3s ease !important;
    }
</style>
""", unsafe_allow_html=True)

# Sidebar - Concepts & Controls
with st.sidebar:
    st.title("📘 Concepts & Controls")
    
    # Gemini API Setup
    st.subheader("🔑 Gemini API Setup")
    gemini_api_key = st.text_input("Enter Gemini API Key", type="password",
                                 help="Get from https://aistudio.google.com/app/apikey")
    
    # Risk Parameters
    st.subheader("⚙️ Risk Parameters")
    low_threshold = st.slider("Low Risk Threshold", 0.0, 0.1, 0.015, 0.001)
    medium_threshold = st.slider("Medium Risk Threshold", 0.0, 0.1, 0.03, 0.001)
    rolling_window = st.slider("Rolling Window (Days)", 5, 90, 30)
    
    # Educational Content
    st.subheader("📚 Key Concepts")
    st.markdown(f"""
    - **Volatility**: Measured via Standard Deviation (SD) of returns
    - **Risk Levels**:
        - 🔴 High: SD > {medium_threshold}
        - 🟡 Medium: {low_threshold} < SD ≤ {medium_threshold}
        - 🟢 Low: SD ≤ {low_threshold}
    - **Rolling Window**: {rolling_window}-day moving volatility
    """)

# Gemini Functions
def generate_gemini_insight(metrics, low, medium, window, start, end):
    """Generate AI-powered market insight using Gemini"""
    if not gemini_api_key:
        return None
        
    genai.configure(api_key=gemini_api_key)
    model = genai.GenerativeModel('gemini-2.0-flash')
    
    prompt = f"""Analyze these stock metrics and provide a 3-4 line investment insight:
    - Tickers: {[m['Ticker'] for m in metrics]}
    - Volatilities: {[m['Volatility (SD)'] for m in metrics]}
    - Risk Levels: {[m['Risk Level'] for m in metrics]}
    - Analysis Period: {start} to {end}
    - Risk Thresholds: Low(<{low}), Medium(<{medium}), High(>{medium})
    - Window: {window}-day rolling
    
    Focus on:
    1. Comparative risk analysis
    2. Market condition implications
    3. Investor recommendations
    Use simple financial terms with emojis."""
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini API Error: {str(e)}")
        return None

# Data Functions
@st.cache_data(ttl=3600)
def load_data(tickers, start, end):
    """Load stock data with progress tracking"""
    with st.spinner("📥 Fetching market data..."):
        return yf.download(tickers, start=start, end=end, group_by='ticker')

def process_ticker(data, ticker, window):
    """Process data for individual ticker"""
    df = data[ticker].copy()
    df['Return'] = df['Close'].pct_change()
    df['Rolling Volatility'] = df['Return'].rolling(window).std()
    df['MA'] = df['Close'].rolling(window).mean()
    return df.dropna()

def risk_assessment(std, low, medium):
    """Determine risk category with dynamic thresholds"""
    if std > medium: return '🔴 High'
    if std > low: return '🟡 Medium'
    return '🟢 Low'

# Main App
st.title("📈 Stock Volatility Analyzer")
st.markdown("### Real-time Risk Analysis using Standard Deviation & Variance")

# Input Controls
col1, col2, col3 = st.columns([2,1,1])
with col1:
    tickers = st.multiselect(
        "Select Stocks", 
        ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'NFLX', 'NVDA', 'META'],
        default=['AAPL', 'MSFT']
    )
with col2:
    start_date = st.date_input("Start Date", datetime(2023,1,1))
with col3:
    end_date = st.date_input("End Date", datetime.today())

# Main Analysis
if tickers:
    try:
        data = load_data(tickers, start_date, end_date + pd.Timedelta(days=1))
        metrics = []
        returns = []

        for ticker in tickers:
            df = process_ticker(data, ticker, rolling_window)
            std = df['Return'].std()
            var = df['Return'].var()
            
            risk = risk_assessment(std, low_threshold, medium_threshold)
            metrics.append({
                'Ticker': ticker,
                'Volatility (SD)': f"{std:.4f}",
                'Variance': f"{var:.6f}",
                'Risk Level': risk
            })
            
            returns.append(df['Return'].rename(ticker))
            
            with st.expander(f"📊 {ticker} Analysis", expanded=True):
                tab1, tab2, tab3 = st.tabs(["Price Action", "Volatility", "Returns"])
                
                with tab1:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Close'], name='Price', line=dict(color='#2c3e50')))
                    fig.add_trace(go.Scatter(x=df.index, y=df['MA'], name=f'{rolling_window}D MA', line=dict(color='#e74c3c')))
                    fig.update_layout(title=f"{ticker} Price & Moving Average", yaxis_title="Price")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab2:
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(x=df.index, y=df['Rolling Volatility'], 
                                       name='Volatility', fill='tozeroy', fillcolor='rgba(231,76,60,0.2)',
                                       line=dict(color='#e74c3c')))
                    fig.update_layout(title=f"{ticker} {rolling_window}-Day Rolling Volatility", yaxis_title="Volatility")
                    st.plotly_chart(fig, use_container_width=True)
                
                with tab3:
                    fig = px.histogram(df, x='Return', nbins=100, 
                                     title=f"Daily Returns Distribution - {ticker}",
                                     color_discrete_sequence=['#3498db'])
                    fig.add_vline(x=std, line_dash="dash", line_color="#e74c3c", 
                                annotation_text=f"SD: {std:.4f}")
                    st.plotly_chart(fig, use_container_width=True)

        # Cross-Asset Analysis
        st.markdown("---")
        st.header("📊 Cross-Asset Analysis")
        
        cols = st.columns(len(metrics))
        for i, col in enumerate(cols):
            with col:
                metric = metrics[i]
                color = "#2ecc71" if "Low" in metric['Risk Level'] else \
                        "#f1c40f" if "Medium" in metric['Risk Level'] else "#e74c3c"
                st.markdown(f"""
                <div class="metric-box">
                    <h3>{metric['Ticker']}</h3>
                    <p style="color:{color}; font-size:1.5rem; margin:0.5rem 0">{metric['Risk Level']}</p>
                    <p>Volatility: {metric['Volatility (SD)']}</p>
                    <p>Variance: {metric['Variance']}</p>
                </div>
                """, unsafe_allow_html=True)
        
        returns_df = pd.concat(returns, axis=1).dropna()
        corr_matrix = returns_df.corr()
        
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("📦 Return Distribution Comparison")
            fig = px.box(returns_df.melt(var_name='Stock'), x='Stock', y='value', 
                       color='Stock', color_discrete_sequence=px.colors.qualitative.Plotly)
            st.plotly_chart(fig, use_container_width=True)
        
        with col2:
            st.subheader("🌡️ Return Correlation Heatmap")
            fig = px.imshow(corr_matrix, text_auto=".2f", color_continuous_scale='RdBu_r',
                          aspect="auto", labels=dict(x="", y="", color="Correlation"))
            st.plotly_chart(fig, use_container_width=True)

        # AI Insights
        if gemini_api_key:
            st.markdown("---")
            st.header("🧠 AI-Powered Market Insight")
            insight = generate_gemini_insight(
                metrics, low_threshold, medium_threshold, 
                rolling_window, start_date, end_date
            )
            if insight:
                st.markdown(f"""
                <div class="gemini-insight">
                    <div style="font-size:1.1rem; color:#2C3E50; line-height:1.6">
                    {insight}
                    </div>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.warning("Could not generate insights. Check API key and try again.")

    except KeyError as e:
        st.error(f"Error loading data for ticker: {e}. Please check the ticker symbol.")
    except Exception as e:
        st.error(f"An error occurred: {str(e)}")

else:
    st.info("👈 Select stocks from the sidebar to begin analysis")