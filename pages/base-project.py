import streamlit as st
import plotly.express as px
import plotly.graph_objects as go    
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np

# own imports
from dataloader import load_data


# ----------------------------
# Page Setup
st.set_page_config(page_title="Base Project Demo", layout="wide")
st.title("Base Project Demo")

# ----------------------------
# Load dataset
df = load_data(name='sp500_close')
meta_df = load_data(name='sp500_meta')

# ----------------------------
# Stock Browser
st.header(":chart_with_upwards_trend: Stock Browser", divider="gray")
st.write("Select a stock ticker from the list to view its price history.")

# ----------------------------
# Create scrollable list of tickers
all_tickers = df.columns.tolist()
selected_ticker = st.selectbox(
    "Choose a stock ticker",
    all_tickers,
    index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers else 0,
)

# Display Meta Information
ticker_meta = meta_df[selected_ticker]

if not ticker_meta.empty:
    st.write(
        f"""
        **Company Name:** {ticker_meta.loc['Company Common Name']}  
        **Sector:** {ticker_meta.loc['TRBC Business Sector Name']}  
        **Exchange Name:** {ticker_meta.loc['Exchange Name']}  
        """
    )
else:
    st.warning("No meta information available for this ticker.")


# Filter data for selected ticker
df_selected = df[[selected_ticker]].copy().dropna()

# Plot using Plotly
fig = px.line(
    df_selected,
    title=f"{selected_ticker} Stock Price",
    labels={"value": "Close Price (USD)", "Date": "Date"},
)

# Show plot
st.plotly_chart(fig, use_container_width=True)


# ----------------------------
# Portfolio Builder


    # ----------------------------
    # Ticker & Allocation Selection


    # ----------------------------
    # Pie Charts of Allocations

        
    # ----------------------------
    # Date Range Selection


    # ----------------------------
    # Compute Net Asse Value Curve


    # ----------------------------
    # Plot NAV of Portfolio vs SPY

    
    # ----------------------------
    # Display Portfolio Metrics

