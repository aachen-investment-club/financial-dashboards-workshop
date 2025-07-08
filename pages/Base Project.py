import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd

from dataloader import load_data

### Base Project
st.set_page_config(page_title="Base Project")
st.title("Hello World!")
st.write("""This is the Base Project!""")

# Load data
df = load_data(cols=['AAPL.OQ'])

# Plot Apple stock price
fig = px.line(
    df, 
    title='Apple Stock Price',
    markers=False
)
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Close Price (USD)',
)
st.title("📈 Apple Stock Price")
st.plotly_chart(fig, use_container_width=True)

