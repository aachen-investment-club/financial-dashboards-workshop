import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

from dataloader import load_data

### Base Project
st.set_page_config(page_title="Interactive Stock Viewer")
st.title("📈 Interactive S&P 500 Stocks Viewer")
st.write("Select a stock ticker from the list to view its price history.")

# Load data
df = load_data()

# Display all available tickers (i.e. DataFrame columns)
all_tickers = df.columns.tolist()

# Create scrollable list of tickers
selected_ticker = st.selectbox(
    "Choose a stock ticker",
    all_tickers,
    index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers else 0,
)

# Filter data for selected ticker
df_selected = df[[selected_ticker]].copy()

# Plot using Plotly
fig = px.line(
    df_selected,
    title=f"{selected_ticker} Stock Price",
    labels={"value": "Close Price (USD)", "Date": "Date"},
)

fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Close Price (USD)",
)

# Show plot
st.plotly_chart(fig, use_container_width=True)