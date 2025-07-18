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
# Stock Browser

st.header(":chart_with_upwards_trend: Stock Browser", divider="gray")
st.write("Select a stock ticker from the list to view its price history.")

# Load data
df = load_data()

# Create scrollable list of tickers
all_tickers = df.columns.tolist()
selected_ticker = st.selectbox(
    "Choose a stock ticker",
    all_tickers,
    index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers else 0,
)

# Filter data for selected ticker
df_selected = df[[selected_ticker]].copy().dropna()

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


# ----------------------------
# Portfolio Construction

st.header(":bar_chart: Portfolio Builder", divider="gray")
st.write("Select tickers, assign weights, and visualize your portfolio performance.")

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
    # Pie Chart of Allocations

    st.subheader("Portfolio Allocation Summary")

    # Create allocation data (including cash)
    allocation_labels = list(weights.keys()) + ["Cash"]
    allocation_values = list(weights.values()) + [cash_weight]

    fig_alloc = px.pie(
        names=allocation_labels,
        values=allocation_values,
        title="Portfolio Allocation",
        hole=0.4,
    )
    fig_alloc.update_traces(textinfo='percent+label')

    st.plotly_chart(fig_alloc, use_container_width=False)

    # ----------------------------
    # Industry Allocation

    st.subheader("Industry Allocation")
    st.write("Industry allocation is not implemented yet.")
    # TODO: Implement industry allocation if data is available


    # ----------------------------
    # Portfolio NAV & SPY
    st.subheader("Portfolio Performance")

    df_selected = df[selected_tickers].copy()
    df_selected = df_selected.dropna(how="any")

    df_norm = df_selected / df_selected.iloc[0]
    nav = sum(df_norm[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
    nav += cash_weight / 100.0
    portfolio_df = pd.DataFrame({"Portfolio Value": nav})

    # SPY
    spy_data = df[["SPY"]].loc[portfolio_df.index[0]:].dropna()
    spy_norm = spy_data / spy_data.iloc[0]
    portfolio_df = portfolio_df.join(spy_norm, how="inner")

    # ----------------------------
    # Daily Returns
    daily_returns = portfolio_df["Portfolio Value"].pct_change().dropna()

    # ----------------------------
    # Combined Figure with Shared X
    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.7, 0.3],
        subplot_titles=("Portfolio vs SPY Benchmark (normalized to 1.0)", "Daily Portfolio Returns")
    )

    # Line Plot Portfolio + SPY
    fig.add_trace(go.Scatter(
        x=portfolio_df.index,
        y=portfolio_df["Portfolio Value"],
        mode='lines',
        name='Your Portfolio',
    ), row=1, col=1)

    fig.add_trace(go.Scatter(
        x=portfolio_df.index,
        y=portfolio_df["SPY"],
        mode='lines',
        name='SPY Benchmark',
    ), row=1, col=1)

    # Daily Returns Bar
    fig.add_trace(go.Bar(
        x=daily_returns.index,
        y=daily_returns.values,
        marker_color=np.where(daily_returns.values >= 0, 'green', 'red'),
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
    
    # Start, End, Holding Period
    start_date = portfolio_df.index.min().date()
    end_date = portfolio_df.index.max().date()
    holding_days = (end_date - start_date).days
    holding_years = holding_days / 365.25

    # Cumulative returns
    cumulative_return = portfolio_df["Portfolio Value"].iloc[-1] - 1.0
    spy_cumulative_return = portfolio_df["Portfolio Value"].iloc[-1] - 1.0

    # Annualized return (CAGR)
    years = (portfolio_df.index[-1] - portfolio_df.index[0]).days / 365.25
    annual_return = (portfolio_df["Portfolio Value"].iloc[-1]) ** (1 / years) - 1

    # Annualized volatility
    annual_volatility = daily_returns.std() * np.sqrt(252)

    # Maximum Drawdown TODO: check if this is correct
    cumulative_max = portfolio_df["Portfolio Value"].cummax()
    drawdown = (portfolio_df["Portfolio Value"] / cumulative_max) - 1.0
    max_drawdown = drawdown.min()

    # Sharpe Ratio (risk-free rate = 0%)
    sharpe_ratio = annual_return / annual_volatility if annual_volatility > 0 else np.nan


    # ----------------------------
    # Display Portfolio Stats


    st.subheader("Holding Info")

    stats_table = pd.DataFrame({
        "Metric": [
            "Start Date",
            "End Date",
            "Holding Period (days)",
            "Holding Period (years)",
        ],
        "Value": [
            f"{start_date}",
            f"{end_date}",
            f"{holding_days}",
            f"~{holding_years:.2f}",
        ]
    })

    st.table(stats_table)



    st.subheader("Risk and Return Metrics")

    metrics_table = pd.DataFrame({
        "Metric": [
            "Annualized Return (CAGR)",
            "Annualized Volatility",
            "Maximum Drawdown",
            "Sharpe Ratio"
        ],
        "Portfolio": [
            f"{annual_return * 100:.2f}%",
            f"{annual_volatility * 100:.2f}%",
            f"{max_drawdown * 100:.2f}%",
            f"{sharpe_ratio:.2f}"
        ],
        "SPY Benchmark": [
            f"{annual_return * 100:.2f}%",
            f"{annual_volatility * 100:.2f}%",
            f"{max_drawdown * 100:.2f}%",
            f"{sharpe_ratio:.2f}"
        ]
    })

    st.table(metrics_table)

else:
    st.info("Please select at least one ticker to begin building your portfolio.")