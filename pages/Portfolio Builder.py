import streamlit as st
import plotly.express as px
import pandas as pd
import numpy as np

# own import
from dataloader import load_data


# ----------------------------
# Page Setup
st.set_page_config(page_title="Portfolio Builder")
st.title("📊 Portfolio Builder")
st.write("Select tickers, assign weights, and visualize your portfolio performance.")


# ----------------------------
# Load Data
df = load_data()
all_tickers = df.columns.tolist()


# ----------------------------
# Portfolio Construction
st.header("Select Tickers")

selected_tickers = st.multiselect(
    "Choose the tickers you want in your portfolio:",
    all_tickers,
    default=["AAPL.OQ"] if "AAPL.OQ" in all_tickers else []
)


weights = {}
total_weight = 0.0


if selected_tickers:
    st.header("Set Allocations (%)")
    cols = st.columns(len(selected_tickers))
    for idx, ticker in enumerate(selected_tickers):
        with cols[idx]:
            weight = st.number_input(
                f"{ticker} (%)", min_value=0.0, max_value=100.0, value=10.0, step=1.0, key=f"{ticker}_weight"
            )
            weights[ticker] = weight

    total_weight = sum(weights.values())
    cash_weight = 100.0 - total_weight

    st.markdown("### 📋 Portfolio Allocation Summary")
    for ticker, weight in weights.items():
        st.write(f"- **{ticker}**: {weight:.1f}%")
    st.write(f"- **Cash**: {cash_weight:.1f}%")

    if total_weight > 100:
        st.error("⚠️ Total stock allocation exceeds 100%. Adjust your weights.")
        st.stop()


    # ----------------------------
    # Portfolio Value Calculation
    st.header("Portfolio Performance")

    df_selected = df[selected_tickers].copy()
    df_selected = df_selected.dropna(how="any")

    # Normalize prices to 1 at start
    df_norm = df_selected / df_selected.iloc[0]

    # Weighted sum
    portfolio = sum(df_norm[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
    portfolio = portfolio * (1 - cash_weight / 100.0) + 1 * (cash_weight / 100.0)

    portfolio_df = pd.DataFrame({"Portfolio Value": portfolio})

    # Plot
    fig = px.line(
        portfolio_df,
        title="Portfolio Value Over Time",
        labels={"index": "Date", "value": "Portfolio Value"},
    )
    fig.update_layout(
        xaxis_title="Date",
        yaxis_title="Portfolio Value (normalized to 1.0)",
    )
    st.plotly_chart(fig, use_container_width=True)

    import plotly.graph_objects as go


    # ----------------------------
    # Holding Period Information
    st.header("Holding Period")

    start_date = portfolio_df.index.min().date()
    end_date = portfolio_df.index.max().date()
    holding_days = (end_date - start_date).days
    holding_years = holding_days / 365.25

    st.write(f"**Start Date:** {start_date}")
    st.write(f"**End Date:** {end_date}")
    st.write(f"**Holding Period:** {holding_days} days (~{holding_years:.2f} years)")


    # ----------------------------
    # Compute Risk Metrics

    # Daily returns
    daily_returns = portfolio_df["Portfolio Value"].pct_change().dropna()

    # Cumulative return
    cumulative_return = portfolio_df["Portfolio Value"].iloc[-1] - 1.0

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
    # Plot: Daily Returns Bar Chart
    st.header("Daily Returns")

    fig_returns = go.Figure()

    fig_returns.add_trace(
        go.Bar(
            x=daily_returns.index,
            y=daily_returns.values,
            marker_color=np.where(daily_returns.values >= 0, 'green', 'red'),
            name='Daily Return'
        )
    )

    fig_returns.update_layout(
        title="Daily Portfolio Returns",
        xaxis_title="Date",
        yaxis_title="Daily Return",
        showlegend=False,
        height=300,
    )

    st.plotly_chart(fig_returns, use_container_width=True)


    # ----------------------------
    # Display Metrics as Table
    st.header("Portfolio Risk Metrics")


    metrics_table = pd.DataFrame({
        "Metric": [
            "Cumulative Return",
            "Annualized Return (CAGR)",
            "Annualized Volatility",
            "Maximum Drawdown",
            "Sharpe Ratio"
        ],
        "Value": [
            f"{cumulative_return * 100:.2f}%",
            f"{annual_return * 100:.2f}%",
            f"{annual_volatility * 100:.2f}%",
            f"{max_drawdown * 100:.2f}%",
            f"{sharpe_ratio:.2f}"
        ]
    })

    st.table(metrics_table)

else:
    st.info("Please select at least one ticker to begin building your portfolio.")