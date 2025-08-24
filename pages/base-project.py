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
# Load data
df = load_data(name='sp500_close')
meta_df = load_data(name='sp500_meta')

# ----------------------------
# Stock Browser

st.header(":chart_with_upwards_trend: Stock Browser", divider="gray")
st.write("Select a stock ticker from the list to view its price history.")

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
st.header(":bar_chart: Portfolio Builder", divider="gray")
st.write("Select tickers, assign weights, and visualize your portfolio performance.")

# Select component
st.subheader("Select Tickers")
selected_tickers = st.multiselect(
    "Choose the tickers you want in your portfolio:",
    all_tickers,
    default=["AAPL.OQ"] if "AAPL.OQ" in all_tickers else []
)

weights = {}
total_weight = 0.0

if selected_tickers:
    st.subheader("Set Allocations")
    cols = st.columns(len(selected_tickers))
    for idx, ticker in enumerate(selected_tickers):
        with cols[idx]:
            weight = st.number_input(
                f"{ticker} (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key=f"{ticker}_weight"
            )
            weights[ticker] = weight

    total_weight = sum(weights.values())
    cash_weight = 100.0 - total_weight

    if total_weight > 100:
        st.error("⚠️ Total stock allocation exceeds 100%. Adjust your weights.")
        st.stop()


    # ----------------------------
    # Pie Charts: Allocation & Industry
    st.subheader("Portfolio Allocation Summary")

    # --- Left Pie Chart: Portfolio Weights ---
    allocation_labels = list(weights.keys()) + ["Cash"]
    allocation_values = list(weights.values()) + [cash_weight]

    fig_alloc = px.pie(
        names=allocation_labels,
        values=allocation_values,
        title="Portfolio Allocation",
        hole=0.4,
    )
    fig_alloc.update_traces(textinfo='percent+label')

    # --- Right Pie Chart: Industry Weights ---

    # Map tickers to industries via meta_df
    industries = []
    for ticker in weights.keys():
        industry = meta_df[ticker].loc["TRBC Business Sector Name"]
        industries.append(industry)

    # Aggregate industry weights
    industry_weight = {}
    for ticker, industry in zip(weights.keys(), industries):
        industry_weight[industry] = industry_weight.get(industry, 0) + weights[ticker]

    # Add cash as its own category
    industry_weight["Cash"] = cash_weight

    fig_industry = px.pie(
        names=list(industry_weight.keys()),
        values=list(industry_weight.values()),
        title="Industry Allocation",
        hole=0.4,
    )
    fig_industry.update_traces(textinfo='percent+label')


    # --- Display side-by-side ---
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_alloc, use_container_width=True)

    with col2:
        st.plotly_chart(fig_industry, use_container_width=True)


    
    # ----------------------------
    # Date Range Selection for Portfolio Evaluation
    st.subheader("Select Evaluation Period")

    min_date = df.index.min().date()
    max_date = df.index.max().date()

    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Start Date",
            value=min_date,
            min_value=min_date,
            max_value=max_date
        )
    with col2:
        end_date = st.date_input(
            "End Date",
            value=max_date,
            min_value=min_date,
            max_value=max_date
        )

    if start_date >= end_date:
        st.error("End date must be after start date.")
        st.stop()
        


    # ----------------------------
    # Compute Net Asse Value 
    st.subheader("Portfolio Performance")

    df_selected = df[selected_tickers].copy()
    df_selected = df_selected.loc[start_date:end_date]
    df_selected = df_selected.dropna(how="any")

    df_norm = df_selected / df_selected.iloc[0]
    nav = sum(df_norm[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
    nav += cash_weight / 100.0
    nav_df = pd.DataFrame({"Portfolio": nav})

    # SPY
    spy_data = df[["SPY"]].loc[start_date:end_date].dropna()  # Ensure SPY data matches the portfolio dates
    spy_norm = spy_data / spy_data.iloc[0]
    nav_df = nav_df.join(spy_norm, how="inner")

    # Daily Returns
    portfolio_returns_daily = nav_df["Portfolio"].pct_change().dropna()

    # ----------------------------
    # Display Portfolio vs SPY Benchmark
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Portfolio vs SPY Benchmark (normalized to 1.0)", "Daily Portfolio Returns")
    )

    # Line Plot Portfolio + SPY
    fig.add_trace(go.Scatter(
        x=nav_df.index,
        y=nav_df["Portfolio"],
        mode='lines',
        name='Your Portfolio',
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=nav_df.index,
        y=nav_df["SPY"],
        mode='lines',
        name='SPY Benchmark',
    ), row=1, col=1)

    # Daily Returns Bar
    fig.add_trace(go.Bar(
        x=portfolio_returns_daily.index,
        y=portfolio_returns_daily.values,
        marker_color=np.where(portfolio_returns_daily.values >= 0, 'green', 'red'),
        name='Daily Returns'
    ), row=2, col=1)

    fig.update_layout(
        height=800,
        legend_title="Legend",
        xaxis=dict(title="Date"),
        yaxis=dict(title="Index"),
        yaxis2=dict(title="Return (%)"),
        showlegend=True,
    )

    st.plotly_chart(fig, use_container_width=True)



    # ----------------------------
    # Compute Metrics
    
    def compute_metrics(nav_df: pd.DataFrame) -> dict:
        
        # Comupute returns
        returns_daily = nav_df.pct_change().dropna()
        cumulative_return = nav_df.iloc[-1] - 1.0

        # Annualized return (CAGR)
        years = (nav_df.index[-1] - nav_df.index[0]).days / 365.25
        annual_return = (nav_df.iloc[-1]) ** (1 / years) - 1

        # Annualized volatility
        annual_volatility = returns_daily.std() * np.sqrt(252)

        # Sharpe Ratio (risk-free rate = 0%)
        sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else np.nan


        return_metrics = {
            "Cumulative Return" : f"{cumulative_return:.2f}x",
            "CAGR" :  f"{annual_return * 100:.2f}%",  # Compound Annual Growth Rate
            "Annualized Volatility" :  f"{annual_volatility * 100:.2f}%",
            "Sharpe Ratio" : f"{sharpe_ratio:.2f}"
        }           
                         
        return return_metrics


    # ----------------------------
    # Display Portfolio Stats
    
    st.subheader("Holding Metrics")

    # compute variables
    start_date = nav_df.index.min().date()
    end_date = nav_df.index.max().date()
    holding_days = (end_date - start_date).days
    holding_years = holding_days / 365.25 

    # print out variables
    st.write(f"**Start Date:** {start_date}")
    st.write(f"**End Date:** {end_date}")
    st.write(f"**Holding Period:** {holding_days} days (~{holding_years:.2f} years)")


    st.subheader("Risk and Return Metrics")

    # compute metrics for portfolio and SPY
    portfolio_return_metrics = compute_metrics(nav_df["Portfolio"])
    spy_return_metrics = compute_metrics(nav_df["SPY"])

    metrics_df = pd.DataFrame([portfolio_return_metrics, spy_return_metrics], index=['Portfolio', 'SPY Benchmark'])
    st.table(metrics_df.T)

else:
    st.info("Please select at least one ticker to begin building your portfolio.")