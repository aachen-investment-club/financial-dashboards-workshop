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
# Market Stress Indicator
st.header(":warning: Market Stress Indicator", divider="red")
st.write("Monitor market volatility and momentum to assess current stress levels.")

def calculate_market_stress_indicator(spy_data, volatility_window=30, momentum_short=10, momentum_long=50):
    """
    Calculate Market Stress Indicator based on Rolling Volatility and Momentum
    
    Parameters:
    - volatility_window: Rolling window for volatility calculation (days)
    - momentum_short: Short-term momentum period (days)
    - momentum_long: Long-term momentum period (days)
    """
    # Calculate daily returns
    spy_returns = spy_data.pct_change().dropna()
    
    # 1. Rolling Volatility (annualized)
    rolling_volatility = spy_returns.rolling(window=volatility_window).std() * np.sqrt(252) * 100
    
    # 2. Momentum Indicator (short MA vs long MA)
    short_ma = spy_data.rolling(window=momentum_short).mean()
    long_ma = spy_data.rolling(window=momentum_long).mean()
    momentum_signal = (short_ma / long_ma - 1) * 100  # Percentage above/below long-term trend
    
    # 3. Volatility Percentile (relative to historical)
    vol_percentile = rolling_volatility.rolling(window=252).rank(pct=True) * 100  # 1-year lookback
    
    # 4. Combined Stress Score (0-100, higher = more stress)
    # Weight: 60% volatility percentile, 40% inverse momentum
    stress_score = (vol_percentile * 0.6) + ((50 - momentum_signal.abs()) * 0.4)
    stress_score = np.clip(stress_score, 0, 100)  # Ensure 0-100 range
    
    return {
        'rolling_volatility': rolling_volatility,
        'momentum_signal': momentum_signal,
        'volatility_percentile': vol_percentile,
        'stress_score': stress_score
    }

# Get SPY data for stress calculation
spy_full_data = df[['SPY']].dropna()
stress_indicators = calculate_market_stress_indicator(spy_full_data['SPY'])

# Date range selector for stress indicator
col1, col2 = st.columns(2)
with col1:
    stress_start_date = st.date_input(
        "Stress Analysis Start Date",
        value=spy_full_data.index.max() - pd.DateOffset(months=12),  # Default: last 12 months
        min_value=spy_full_data.index.min().date(),
        max_value=spy_full_data.index.max().date(),
        key="stress_start"
    )
with col2:
    stress_end_date = st.date_input(
        "Stress Analysis End Date",
        value=spy_full_data.index.max().date(),
        min_value=spy_full_data.index.min().date(),
        max_value=spy_full_data.index.max().date(),
        key="stress_end"
    )

if stress_start_date >= stress_end_date:
    st.error("End date must be after start date.")
else:
    # Filter data for selected period (filter each indicator separately to avoid index mismatch)
    filtered_data = {}
    for key, values in stress_indicators.items():
        # Use datetime-based filtering instead of boolean mask to avoid length mismatches
        mask = (values.index.date >= stress_start_date) & (values.index.date <= stress_end_date)
        filtered_data[key] = values[mask].dropna()
    
    # Current stress level (most recent value)
    current_stress = filtered_data['stress_score'].iloc[-1] if len(filtered_data['stress_score']) > 0 else 0
    current_volatility = filtered_data['rolling_volatility'].iloc[-1] if len(filtered_data['rolling_volatility']) > 0 else 0
    current_momentum = filtered_data['momentum_signal'].iloc[-1] if len(filtered_data['momentum_signal']) > 0 else 0
    
    # Stress level interpretation
    if current_stress < 30:
        stress_level = "🟢 Low Stress"
        stress_color = "green"
        stress_description = "Market is relatively calm with low volatility"
    elif current_stress < 60:
        stress_level = "🟡 Medium Stress"
        stress_color = "orange" 
        stress_description = "Market showing moderate volatility signals"
    else:
        stress_level = "🔴 High Stress"
        stress_color = "red"
        stress_description = "Market experiencing elevated volatility and stress"
    
    # Display current stress metrics
    st.subheader("Current Market Conditions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Stress Score",
            f"{current_stress:.1f}/100",
            help="Combined stress indicator (0=calm, 100=extreme stress)"
        )
        st.markdown(f"**{stress_level}**")
        st.write(stress_description)
    
    with col2:
        st.metric(
            "Rolling Volatility",
            f"{current_volatility:.1f}%",
            help="30-day rolling volatility (annualized)"
        )
    
    with col3:
        momentum_color = "green" if current_momentum > 0 else "red"
        st.metric(
            "Momentum Signal",
            f"{current_momentum:+.1f}%",
            help="Short-term vs Long-term trend strength"
        )
    
    with col4:
        vol_percentile = filtered_data['volatility_percentile'].iloc[-1] if len(filtered_data['volatility_percentile']) > 0 else 0
        st.metric(
            "Vol. Percentile",
            f"{vol_percentile:.0f}%",
            help="Current volatility vs 1-year history"
        )

    # Stress indicator charts
    st.subheader("Stress Indicator Timeline")
    
    # Create subplots
    fig_stress = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.05,
        row_heights=[0.4, 0.3, 0.3],
        subplot_titles=(
            "Market Stress Score (0-100)",
            "Rolling 30-Day Volatility (%)",
            "Momentum Signal (%)"
        )
    )
    
    # Stress score with color zones
    fig_stress.add_trace(go.Scatter(
        x=filtered_data['stress_score'].index,
        y=filtered_data['stress_score'],
        mode='lines',
        name='Stress Score',
        line=dict(color='purple', width=2),
        fill='tonexty'
    ), row=1, col=1)
    
    # Add stress level zones
    fig_stress.add_hline(y=30, line_dash="dash", line_color="green", opacity=0.5, row=1, col=1)
    fig_stress.add_hline(y=60, line_dash="dash", line_color="orange", opacity=0.5, row=1, col=1)
    
    # Rolling Volatility
    fig_stress.add_trace(go.Scatter(
        x=filtered_data['rolling_volatility'].index,
        y=filtered_data['rolling_volatility'],
        mode='lines',
        name='30-Day Volatility',
        line=dict(color='red', width=1.5)
    ), row=2, col=1)
    
    # Momentum Signal
    fig_stress.add_trace(go.Scatter(
        x=filtered_data['momentum_signal'].index,
        y=filtered_data['momentum_signal'],
        mode='lines',
        name='Momentum',
        line=dict(color='blue', width=1.5)
    ), row=3, col=1)
    
    # Add zero line for momentum
    fig_stress.add_hline(y=0, line_dash="solid", line_color="gray", opacity=0.3, row=3, col=1)
    
    fig_stress.update_layout(
        height=700,
        title_text="Market Stress Analysis Dashboard",
        showlegend=False
    )
    
    fig_stress.update_xaxes(title_text="Date", row=3, col=1)
    fig_stress.update_yaxes(title_text="Stress Level", row=1, col=1, range=[0, 100])
    fig_stress.update_yaxes(title_text="Volatility %", row=2, col=1)
    fig_stress.update_yaxes(title_text="Momentum %", row=3, col=1)
    
    st.plotly_chart(fig_stress, use_container_width=True)
    
    # Interpretation guide
    with st.expander("📖 How to Interpret the Market Stress Indicator"):
        st.markdown("""
        **Stress Score Components:**
        
        🎯 **Stress Score (0-100):**
        - **0-30**: 🟢 Low stress - Market calm, good for risk-taking
        - **30-60**: 🟡 Medium stress - Moderate caution advised  
        - **60-100**: 🔴 High stress - High volatility, defensive positioning
        
        📈 **Rolling Volatility:**
        - Measures 30-day price swings (annualized)
        - Higher = more unpredictable price movements
        - Normal range: 10-25% for SPY
        
        ⚡ **Momentum Signal:**
        - Compares short-term (10-day) vs long-term (50-day) trend
        - **Positive**: Short-term strength (bullish momentum)
        - **Negative**: Short-term weakness (bearish momentum)
        
        💡 **Usage Tips:**
        - High stress periods often present buying opportunities for long-term investors
        - Consider reducing position sizes during high stress periods
        - Use momentum signals to time entries/exits within your strategy
        """)

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
    # Volatility Targeting Strategy
    st.subheader("🎯 Volatility Targeting")
    
    volatility_targeting_enabled = st.checkbox(
        "Enable Volatility Targeting", 
        value=False, 
        help="Dynamically adjust portfolio exposure to maintain a target volatility level"
    )
    
    if volatility_targeting_enabled:
        st.info("""
        **How Volatility Targeting Works:**
        - Portfolio exposure is scaled up/down based on realized volatility vs. target
        - When volatility is low → increase exposure (take more risk)
        - When volatility is high → decrease exposure (reduce risk)  
        - This creates a counter-cyclical risk management approach
        """)
        
        # Target volatility input
        col1, col2, col3 = st.columns(3)
        
        with col1:
            target_volatility = st.slider(
                "Target Volatility (%)", 
                min_value=5.0, 
                max_value=25.0, 
                value=12.0, 
                step=0.5,
                help="Annual target volatility for the portfolio"
            )
        
        with col2:
            volatility_lookback = st.slider(
                "Volatility Lookback (days)", 
                min_value=10, 
                max_value=60, 
                value=22, 
                step=1,
                help="Rolling window for volatility calculation"
            )
        
        with col3:
            max_leverage = st.slider(
                "Max Leverage", 
                min_value=0.5, 
                max_value=2.0, 
                value=1.5, 
                step=0.1,
                help="Maximum portfolio exposure (>1.0 allows leverage)"
            )
        
        def calculate_volatility_targeted_nav(nav_series, target_vol, vol_window, max_lev):
            """Calculate NAV with volatility targeting"""
            returns = nav_series.pct_change().dropna()
            
            # Calculate rolling volatility (annualized)
            rolling_vol = returns.rolling(window=vol_window).std() * np.sqrt(252) * 100
            
            # Calculate scaling factor (target vol / realized vol)
            scaling_factor = target_vol / rolling_vol
            
            # Apply leverage constraints
            scaling_factor = np.clip(scaling_factor, 0.1, max_lev)
            
            # Calculate volatility-targeted returns
            vol_targeted_returns = returns * scaling_factor.shift(1)  # Use previous day's scaling
            
            # Calculate NAV (starting at 1.0)
            vol_targeted_nav = (1 + vol_targeted_returns).cumprod()
            vol_targeted_nav.iloc[0] = 1.0  # Ensure it starts at 1.0
            
            return vol_targeted_nav, rolling_vol, scaling_factor
        
        # Calculate volatility targeted portfolio
        vol_targeted_nav, rolling_volatility, scaling_factors = calculate_volatility_targeted_nav(
            nav_df["Portfolio"], target_volatility, volatility_lookback, max_leverage
        )
        
        # Create comprehensive comparison
        vol_comparison_df = nav_df[["Portfolio", "SPY"]].copy()
        vol_comparison_df["Portfolio (Vol Targeted)"] = vol_targeted_nav
        
        # Volatility targeting visualization
        fig_vol_target = make_subplots(
            rows=3, cols=1,
            shared_xaxes=True,
            vertical_spacing=0.05,
            row_heights=[0.5, 0.25, 0.25],
            subplot_titles=(
                "Portfolio Performance Comparison",
                "Rolling Portfolio Volatility (%)",
                "Volatility Scaling Factor"
            )
        )
        
        # Performance comparison
        fig_vol_target.add_trace(go.Scatter(
            x=vol_comparison_df.index,
            y=vol_comparison_df["Portfolio"],
            mode='lines',
            name='Original Portfolio',
            line=dict(color='blue', width=2)
        ), row=1, col=1)
        
        fig_vol_target.add_trace(go.Scatter(
            x=vol_comparison_df.index,
            y=vol_comparison_df["Portfolio (Vol Targeted)"],
            mode='lines',
            name='Vol Targeted Portfolio',
            line=dict(color='green', width=2)
        ), row=1, col=1)
        
        fig_vol_target.add_trace(go.Scatter(
            x=vol_comparison_df.index,
            y=vol_comparison_df["SPY"],
            mode='lines',
            name='SPY Benchmark',
            line=dict(color='gray', width=1, dash='dash')
        ), row=1, col=1)
        
        # Rolling volatility with target line
        fig_vol_target.add_trace(go.Scatter(
            x=rolling_volatility.index,
            y=rolling_volatility,
            mode='lines',
            name='Realized Volatility',
            line=dict(color='red', width=1.5),
            showlegend=False
        ), row=2, col=1)
        
        # Add target volatility line
        fig_vol_target.add_hline(
            y=target_volatility, 
            line_dash="solid", 
            line_color="orange", 
            opacity=0.8,
            row=2, col=1
        )
        
        # Scaling factor
        fig_vol_target.add_trace(go.Scatter(
            x=scaling_factors.index,
            y=scaling_factors,
            mode='lines',
            name='Scaling Factor',
            line=dict(color='purple', width=1.5),
            fill='tonexty',
            showlegend=False
        ), row=3, col=1)
        
        # Add 1.0 reference line for scaling
        fig_vol_target.add_hline(
            y=1.0, 
            line_dash="solid", 
            line_color="gray", 
            opacity=0.5,
            row=3, col=1
        )
        
        fig_vol_target.update_layout(
            height=800,
            title_text=f"Volatility Targeting Analysis (Target: {target_volatility}%)",
            showlegend=True
        )
        
        fig_vol_target.update_xaxes(title_text="Date", row=3, col=1)
        fig_vol_target.update_yaxes(title_text="Portfolio Value", row=1, col=1)
        fig_vol_target.update_yaxes(title_text="Volatility %", row=2, col=1)
        fig_vol_target.update_yaxes(title_text="Scaling Factor", row=3, col=1)
        
        st.plotly_chart(fig_vol_target, use_container_width=True)
        
        # Volatility targeting metrics
        st.subheader("Volatility Targeting Results")
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            original_final = vol_comparison_df["Portfolio"].iloc[-1]
            st.metric(
                "Original Portfolio", 
                f"{original_final:.3f}x",
                f"{(original_final - 1) * 100:.2f}%"
            )
        
        with col2:
            vol_targeted_final = vol_comparison_df["Portfolio (Vol Targeted)"].iloc[-1]
            st.metric(
                "Vol Targeted Portfolio", 
                f"{vol_targeted_final:.3f}x",
                f"{(vol_targeted_final - 1) * 100:.2f}%"
            )
        
        with col3:
            vol_impact = vol_targeted_final - original_final
            st.metric(
                "Vol Targeting Impact", 
                f"{vol_impact:+.3f}x",
                f"{vol_impact * 100:+.2f}%"
            )
        
        with col4:
            avg_realized_vol = rolling_volatility.mean()
            st.metric(
                "Avg Realized Vol", 
                f"{avg_realized_vol:.1f}%",
                f"{avg_realized_vol - target_volatility:+.1f}% vs target"
            )
        
        # Detailed volatility statistics
        with st.expander("📊 Detailed Volatility Statistics"):
            vol_stats_df = pd.DataFrame({
                'Metric': [
                    'Target Volatility',
                    'Average Realized Volatility',
                    'Volatility Standard Deviation',
                    'Time Above Target (%)',
                    'Time Below Target (%)',
                    'Average Scaling Factor',
                    'Max Scaling Factor',
                    'Min Scaling Factor'
                ],
                'Value': [
                    f"{target_volatility:.1f}%",
                    f"{rolling_volatility.mean():.1f}%",
                    f"{rolling_volatility.std():.1f}%",
                    f"{(rolling_volatility > target_volatility).mean() * 100:.1f}%",
                    f"{(rolling_volatility < target_volatility).mean() * 100:.1f}%",
                    f"{scaling_factors.mean():.2f}x",
                    f"{scaling_factors.max():.2f}x",
                    f"{scaling_factors.min():.2f}x"
                ]
            })
            st.table(vol_stats_df)
        
        # Strategy explanation
        with st.expander("📖 Understanding Volatility Targeting"):
            st.markdown(f"""
            **Strategy Mechanics:**
            
            🎯 **Target Volatility**: {target_volatility}% annually
            - Portfolio exposure is scaled to maintain this volatility level
            - Scaling Factor = Target Vol / Realized Vol
            
            📈 **Risk Scaling:**
            - **High volatility periods**: Reduce exposure (scaling < 1.0)
            - **Low volatility periods**: Increase exposure (scaling > 1.0)  
            - **Max leverage limit**: {max_leverage}x to control risk
            
            ⚖️ **Benefits:**
            - **Smoother returns**: More consistent risk profile over time
            - **Counter-cyclical**: Natural buy-low-sell-high behavior
            - **Risk management**: Automatic position sizing based on market conditions
            
            ⚠️ **Considerations:**
            - May underperform in strong trending markets
            - Transaction costs not included in this simulation
            - Leverage >1.0 requires margin/derivatives access
            
            **Interpretation:**
            - Green line above blue = Vol targeting outperformed
            - Scaling factor >1.0 = Taking more risk (leveraging up)
            - Scaling factor <1.0 = Reducing risk (scaling down)
            """)

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