import streamlit as st
import plotly.express as px
import numpy as np
import pandas as pd


st.set_page_config(page_title="Team 1's subpage")

st.title("Welcome to team 1's subpage!")



st.write("""
This is team 1's subpage!
""")


np.random.seed(42)
df = pd.DataFrame({
    'x': np.arange(1, 11),
    'y': np.linspace(1,1000,10)
})

fig = px.line(
    df, 
    x='x', 
    y='y', 
    title='AIC portfolio value',
    markers=True
)

fig.update_layout(
    xaxis_title='Time',
    yaxis_title='euro',
)

st.title("📈 AIC portfolio value")

st.plotly_chart(fig, use_container_width=True)