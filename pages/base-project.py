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
# Load dataset
df = load_data(name='sp500_close')
meta_df = load_data(name='sp500_meta')

# ----------------------------
# Stock Comparison
st.header(":chart_with_upwards_trend: Stock Comparison", divider="gray")
st.write("Select one or more stock tickers to compare their price history.")

# Initialize stock list in session state
if "stock_list" not in st.session_state:
    st.session_state.stock_list = [0]  # Start with one stock (ID 0)
if "next_stock_id" not in st.session_state:
    st.session_state.next_stock_id = 1

all_tickers = df.columns.tolist()
selected_tickers = []

# Display each stock with remove button
for stock_id in st.session_state.stock_list:
    col1, col2 = st.columns([4, 1])
    
    with col1:
        ticker = st.selectbox(
            f"Stock {stock_id + 1}",
            all_tickers,
            index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers and stock_id == 0 else 0,
            key=f"stock_select_{stock_id}",
        )
        if ticker not in selected_tickers:
            selected_tickers.append(ticker)
    
    with col2:
        # Add vertical spacing to align button with selectbox
        st.markdown("<br>", unsafe_allow_html=True)
        # Only show remove button if there's more than one stock
        if len(st.session_state.stock_list) > 1:
            if st.button("🗑️", key=f"remove_{stock_id}", help="Remove this stock"):
                st.session_state.stock_list.remove(stock_id)
                st.rerun()

# Button to add another stock
if st.button("➕ Add another stock"):
    st.session_state.stock_list.append(st.session_state.next_stock_id)
    st.session_state.next_stock_id += 1
    st.rerun()

# Show Meta Information for all selected tickers
st.subheader("Company Information")
for ticker in selected_tickers:
    ticker_meta = meta_df[ticker]
    if not ticker_meta.empty:
        st.markdown(
            f"""
            **{ticker}**  
            - Company: {ticker_meta.loc['Company Common Name']}  
            - Sector: {ticker_meta.loc['TRBC Business Sector Name']}  
            - Exchange: {ticker_meta.loc['Exchange Name']}  
            """
        )
    else:
        st.warning(f"No meta info for {ticker}")

# Plot the selected tickers
df_selected = df[selected_tickers].copy().dropna()

fig = px.line(
    df_selected,
    title="Selected Stock Prices",
    labels={"value": "Close Price (USD)", "Date": "Date"},
)

st.plotly_chart(fig, use_container_width=True)

# Display Meta Information
ticker_meta = meta_df[selected_tickers]

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
cash_weight = 0.0

if selected_tickers:
    st.subheader("Set Allocations")

    equal_weights = st.checkbox("Rebalance equally", value=True)

    if equal_weights:
        # Equal allocation to all selected tickers
        weight_per_ticker = 100.0 / len(selected_tickers)
        weights = {ticker: weight_per_ticker for ticker in selected_tickers}
        total_weight = sum(weights.values())
        cash_weight = 100.0 - total_weight
        st.info(f"Each ticker is assigned {weight_per_ticker:.2f}% of the portfolio.")
    else:
        # Manual input
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
    # Monthly Rebalancing Analysis
    st.subheader("📊 Buy & Hold vs Monthly Rebalancing")
    
    rebalancing_enabled = st.checkbox(
        "Enable Monthly Rebalancing Analysis", 
        value=False, 
        help="Compare your Buy & Hold strategy with monthly rebalancing to target weights"
    )
    
    if rebalancing_enabled:
        st.info("""
        **How Monthly Rebalancing Works:**
        - Every month, the portfolio is rebalanced back to your target allocation
        - This means selling winners and buying losers to maintain desired weights
        - Rebalancing can reduce volatility but may also limit upside in trending markets
        """)
        
        def calculate_monthly_rebalanced_nav(df_prices, weights, cash_weight, start_date, end_date):
            """Calculate NAV with monthly rebalancing"""
            df_selected = df_prices[selected_tickers].copy()
            df_selected = df_selected.loc[start_date:end_date].dropna()
            
            # Get monthly rebalancing dates (first day of each month)
            rebalance_dates = pd.date_range(start=df_selected.index[0], end=df_selected.index[-1], freq='MS')
            rebalance_dates = [date for date in rebalance_dates if date in df_selected.index]
            
            nav_rebalanced = []
            current_nav = 1.0  # Start with $1
            
            for i, date in enumerate(df_selected.index):
                if i == 0:
                    # Initialize portfolio
                    nav_rebalanced.append(current_nav)
                    continue
                
                prev_date = df_selected.index[i-1]
                
                # Calculate daily return for each stock
                daily_returns = df_selected.loc[date] / df_selected.loc[prev_date] - 1
                
                # If it's a rebalancing date, reset to target weights
                if date in rebalance_dates:
                    # Portfolio return since last rebalancing
                    portfolio_return = sum(daily_returns[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
                    current_nav = current_nav * (1 + portfolio_return)
                    # Reset to target allocation (rebalancing happens)
                else:
                    # Regular day - portfolio drifts with individual stock performance
                    portfolio_return = sum(daily_returns[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
                    current_nav = current_nav * (1 + portfolio_return)
                
                nav_rebalanced.append(current_nav)
            
            return pd.Series(nav_rebalanced, index=df_selected.index), rebalance_dates
        
        # Calculate rebalanced portfolio
        rebalanced_nav, rebalance_dates = calculate_monthly_rebalanced_nav(df, weights, cash_weight, start_date, end_date)
        
        # Create comparison dataframe
        comparison_df = nav_df[["Portfolio", "SPY"]].copy()
        comparison_df["Portfolio (Rebalanced)"] = rebalanced_nav
        
        # Comparison chart
        fig_comparison = go.Figure()
        
        # Add Buy & Hold
        fig_comparison.add_trace(go.Scatter(
            x=comparison_df.index,
            y=comparison_df["Portfolio"],
            mode='lines',
            name='Buy & Hold',
            line=dict(color='blue')
        ))
        
        # Add Rebalanced
        fig_comparison.add_trace(go.Scatter(
            x=comparison_df.index,
            y=comparison_df["Portfolio (Rebalanced)"],
            mode='lines',
            name='Monthly Rebalanced',
            line=dict(color='orange')
        ))
        
        # Add SPY for reference
        fig_comparison.add_trace(go.Scatter(
            x=comparison_df.index,
            y=comparison_df["SPY"],
            mode='lines',
            name='SPY Benchmark',
            line=dict(color='gray', dash='dash')
        ))
        
        # Add rebalancing markers
        rebalance_values = [comparison_df.loc[date, "Portfolio (Rebalanced)"] for date in rebalance_dates if date in comparison_df.index]
        fig_comparison.add_trace(go.Scatter(
            x=[date for date in rebalance_dates if date in comparison_df.index],
            y=rebalance_values,
            mode='markers',
            name='Rebalancing Dates',
            marker=dict(color='red', size=8, symbol='diamond'),
            hovertemplate='Rebalanced on %{x}<extra></extra>'
        ))
        
        fig_comparison.update_layout(
            title="Portfolio Strategies Comparison (Normalized to 1.0)",
            xaxis_title="Date",
            yaxis_title="Portfolio Value",
            height=600,
            hovermode='x unified'
        )
        
        st.plotly_chart(fig_comparison, use_container_width=True)
        
        # Rebalancing summary
        st.subheader("Rebalancing Summary")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            final_buyhold = comparison_df["Portfolio"].iloc[-1]
            st.metric(
                "Buy & Hold Final Value", 
                f"{final_buyhold:.3f}x",
                f"{(final_buyhold - 1) * 100:.2f}%"
            )
        
        with col2:
            final_rebalanced = comparison_df["Portfolio (Rebalanced)"].iloc[-1]
            st.metric(
                "Rebalanced Final Value", 
                f"{final_rebalanced:.3f}x",
                f"{(final_rebalanced - 1) * 100:.2f}%"
            )
        
        with col3:
            difference = final_rebalanced - final_buyhold
            st.metric(
                "Rebalancing Impact", 
                f"{difference:+.3f}x",
                f"{difference * 100:+.2f}%"
            )
        
        # Show rebalancing dates
        with st.expander(f"📅 Rebalancing Dates ({len(rebalance_dates)} total)"):
            st.write("The portfolio was rebalanced on the following dates:")
            rebalance_df = pd.DataFrame({
                'Rebalancing Date': [date.strftime('%Y-%m-%d') for date in rebalance_dates if date in comparison_df.index],
                'Portfolio Value': [f"{comparison_df.loc[date, 'Portfolio (Rebalanced)']:.3f}x" for date in rebalance_dates if date in comparison_df.index]
            })
            st.dataframe(rebalance_df, use_container_width=True)

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