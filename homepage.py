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

_ = load_data()
