import streamlit as st
from dataloader import load_data

st.set_page_config(
    page_title="Financial Dashboards Workshop",
    page_icon="📊",
    layout="wide",
)

st.title("Home")
st.write("""
Welcome to the Dahsboards Workshop!
- checkout the guide in ...
""")

# preload datasets in cache
_ = load_data(name='sp500_close')
_ = load_data(name='sp500_meta')
