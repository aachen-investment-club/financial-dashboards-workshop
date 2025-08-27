import streamlit as st
from dataloader import load_data


# --- Page Config ---
st.set_page_config(page_title="AIC - Financial Dashboards", page_icon="📊", layout="wide")

# --- Title & Intro ---
st.title("📊 AIC - Financial Dashboards")
st.markdown(
    """
    Welcome to **Aachen Investment Club's Financial Dashboards**! 
    This platform showcases the results of our **Financial Dashboards Workshop**.  

    Here, we bring together the creativity and insights of our members by merging their dashboards into one hub.  
    """
)

st.divider()

# --- Highlight Boxes ---
col1, col2, col3 = st.columns(3)

with col1:
    st.success("✅ Explore the **Base Project**")
    st.markdown("[Open Base Project](/base-project)")

with col2:
    st.info("💻 Contribute on **GitHub**")
    st.markdown("[View our Repository](https://github.com/aachen-investment-club/financial-dashboards-workshop)")

with col3:
    st.warning("🌍 Learn more about **AIC**")
    st.markdown("[Visit our Website](https://www.aachen-investment-club.de/)")

st.divider()



# preload datasets in cache
_ = load_data(name='sp500_close')
_ = load_data(name='sp500_meta')
