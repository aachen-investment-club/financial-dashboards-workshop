import streamlit as st
from dataloader import load_data

st.set_page_config(
    page_title="Financial Dashboards Workshop",
    page_icon="📊",
    layout="wide",
)

st.title("AIC - Financial Dashboards")
st.write("""
        Welcome to AIC's financial dashboads!

        In this website, we contain the results of the financial dashboards workshop.     
         
        We will merge your dashboards into this website. 
        """)

base_project_url = "/base-project"
repo_url = "https://github.com/aachen-investment-club/financial-dashboards-workshop"
aic_url = "https://www.aachen-investment-club.de/"


st.markdown(f"Checkout the base project: [base project](%s)" % base_project_url)

st.markdown(f"Checkout the GitHub repository: [repo](%s)" % repo_url)


st.markdown(f"Checkout our Website: [our website](%s)" % aic_url)


# preload datasets in cache
_ = load_data(name='sp500_close')
_ = load_data(name='sp500_meta')
