![AIC](../images/aic_banner.png)

# 3) Base Project: Portfolio Builder

From this section on, we will focus on dashboard creation. First, you will work on the base project alone. This will be portfolio builder tool, which you can use to simulate how certain allocations from single stocks historically performed against the S&P 500 index.

The goal of this section is to introduce you to building dashboards with streamlit & plotly and further provide an example use case for git. Therefore at the end of this section you will be assigned to a team and practice merging all of your branches into one. In this section you are not expected to show creativity, just be quick in understanding the code. In the final merge step you will most likely encounter some merge conflicts and we will use it as a practice to resolve them.

Follow these instructions to build your base project: 
1. Paste a single code block.
2. Read the code, try to understand it.
2. Save your file (or turn on auto-save).
3. Refresh your website and try to spot the changes; associate them with your code.

## Dataset & Dataloader
Go to the file [../pages/base-project.py](../pages/base-project.py). You will work here for the rest of this task.

We already took care of curating the dataset for you. The `load_data` function was implemented for this, which is imported at the top of your file from [dataloader.py](../dataloader.py).

**Important Reminder**
You need to create the ``.env`` file as described in the [setup guide](../guide/1_setup.md) to access our datasets.

Once you start the app the dataloader will first download the datasets in the ``data`` directory and store it inside a cached variable.

We provide you with following datasets:
- ``sp500_close.csv`` contains close prices of all S&P 500 stocks, recent delistings excluded, and the SPDR S&P 500 ETF Trust with symbol ``SPY`` from 2000-01-03 until 2025-07-18
- ``sp500_meta.csv`` includes meta data for all stocks: Company Common Name, TRBC Business Sector Name, Exchange Name


## Stock Browser

Before starting with the portfolio builder, lets write a little tool to explore our dataset.

Setup the page.
```py
st.set_page_config(page_title="Base Project", layout="wide")
st.title("Base Project")
```

Initialize the datasets.
```py
df = load_data(name='sp500_close')
meta_df = load_data(name='sp500_meta')
```

Next, we build the a select box for the stock browser. This component will list out all the available stocks in the S&P500, and let you choose one of them for visualization.

```py
# Page title
st.header(":chart_with_upwards_trend: Stock Browser", divider="gray")
st.write("Select a stock ticker from the list to view its price history.")

# Create scrollable list of tickers
all_tickers = df.columns.tolist()
selected_ticker = st.selectbox(
    "Choose a stock ticker",
    all_tickers,
    index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers else 0,
)
```

Now the user input is stored in the `selected_ticker` variable. Let's search our meta dataset first and output as text
```py
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
```

Finally we create a plotly plot to display the close price of our `selected_ticker`.

```py
# Filter close price data for selected ticker
df_selected = df[[selected_ticker]].copy().dropna()

# Create figure using Plotly
fig = px.line(
    df_selected,
    title=f"{selected_ticker} Stock Price",
    labels={"value": "Close Price (USD)", "Date": "Date"},
)

# Plot figure on our dashboard
st.plotly_chart(fig, use_container_width=True)
```

Well done! If everything worked properly, you should have a working S&P500 stock viewer. Make sure to play around with it, before proceeding ;). 



## Portfolio Builder
Next, we proceed with the portfolio builder. Again setup the title.

```py
st.header(":bar_chart: Portfolio Builder", divider="gray")
st.write("Select tickers, assign weights, and visualize your portfolio performance.")

```

### Multiselect for Ticker & Weights Input
Insert a multiselect component that allows you to select at least one stock. Note that this returns a list of ``selected_tickers``!

```py
# Select component
st.subheader("Select Tickers")
selected_tickers = st.multiselect(
    "Choose the tickers you want in your portfolio:",
    all_tickers,
    default=["AAPL.OQ"] if "AAPL.OQ" in all_tickers else []
)
```

Next, we create a component to select the weights that you will assign to each stock.

```py
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

    # --- Paste all following code blocks inside here  --- #


    # ---------------------------------------------------- #
    
else:
    st.info("Please select at least one ticker to begin building your portfolio.")
```

### Allocation Pie Charts

For nice visualization, lets plot our portfolio weights in two pie charts. 
- The left pie chart dispays **portfolio weights**
- And the right one **industry wieghts**

Lets start with portfolio weights. Still inside the inside if statement from the last block, paste the following:

```py
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
```

And now the industry weights

```py
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
```

Now we created both figures. Let's include them on our website.
```py
    # --- Display side-by-side ---
    col1, col2 = st.columns(2)

    with col1:
        st.plotly_chart(fig_alloc, use_container_width=True)

    with col2:
        st.plotly_chart(fig_industry, use_container_width=True)
```

### Portfolio Performance

Now its time for the serious stuff - plotting our portfolio's performance. Not to make it too easy for you, we want the flexibility to select the period on which the portfolio is evaluated. To conclude we require following steps:
1. Date range selection for portfolio evaluation
2. Compute net asset value (NAV) and daily portfolio returns
3. Display portfolio NAV against the SPY Benchmark

Start with step one **Data Range Selection**
```py
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
```

Now step two **Net Asset Value & Daily Returns**. Note that we both norm the portfolio return and the SPY benchmark such that both curves start at 1 to make them comparable.

```py
    st.subheader("Portfolio Performance")

    # Filter only selected tickers and the selected date range 
    df_selected = df[selected_tickers].copy()
    df_selected = df_selected.loc[start_date:end_date]
    df_selected = df_selected.dropna(how="any")

    # Compute Portfolio NAV
    df_norm = df_selected / df_selected.iloc[0]
    nav = sum(df_norm[ticker] * (weights[ticker] / 100.0) for ticker in selected_tickers)
    nav += cash_weight / 100.0
    nav_df = pd.DataFrame({"Portfolio": nav})

    # Compute SPY NAV
    spy_data = df[["SPY"]].loc[start_date:end_date].dropna()
    spy_norm = spy_data / spy_data.iloc[0]
    nav_df = nav_df.join(spy_norm, how="inner")

    # Daily Returns
    portfolio_returns_daily = nav_df["Portfolio"].pct_change().dropna()
```

Finally it's time for plotting. We will plot two subplots with a shared x axis. Just copy and paste and see how it looks like :)

```py
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
```

Great work! We are nearly finished. But we wouldn't be good investors if we only look at charts and see the money printer goes brrrr :rocket::money_with_wings:

As opposed to all the delusional day trading gurus, we are very sceptical and demand a more nuanced assessment. :detective:

### Performance Metrics

Let's start simple and look at our holding period. 
```py
    st.subheader("Holding Period")

    # compute variables
    start_date = nav_df.index.min().date()
    end_date = nav_df.index.max().date()
    holding_days = (end_date - start_date).days
    holding_years = holding_days / 365.25 

    # print out variables
    st.write(f"**Start Date:** {start_date}")
    st.write(f"**End Date:** {end_date}")
    st.write(f"**Holding Period:** {holding_days} days (~{holding_years:.2f} years)")
```

But now for the interesting part we will create a function `compute_metrics` that takes a net asset value curve as input und returns a ready to plot dictionary. We will apply this function to both NAV curves (Portfolio & SPY) seperately.


```py
def compute_metrics(nav_df: pd.DataFrame) -> dict:
    
    # Comupute metrics
    returns_daily = nav_df.pct_change().dropna()
    
    # Prepare metrics in dict format
    return_metrics = {
        "Cumulative Return" : f"{cumulative_return:.2f}x",
        "CAGR" :  f"{annual_return * 100:.2f}%",  # Compound Annual Growth Rate
        "Annualized Volatility" :  f"{annual_volatility * 100:.2f}%",
        "Sharpe Ratio" : f"{sharpe_ratio:.2f}"
    }           
                        
    return return_metrics
```

OOPS! :dizzy_face: Something is missing. :sweat_smile: Somehow I forgot how to compute the risk metrics. Maybe I am not good enought to be a serious investor... :disappointed: But you have the potential! As long as you did not forget how to use your brain after all the copy and pasting.

Compute the variables `cumulative_return`, `annual_return`, `annual_volatility`, and `sharpe_ratio` inside the function `compute_metrics`. Feel free to browse the internet for this step. Note you can assume a risk free rate of 0% for calculating the sharpe ratio.

Once you are done, plot it with

```py
    st.subheader("Risk and Return Metrics")

    # compute metrics for portfolio and SPY
    portfolio_return_metrics = compute_metrics(nav_df["Portfolio"])
    spy_return_metrics = compute_metrics(nav_df["SPY"])

    metrics_df = pd.DataFrame([portfolio_return_metrics, spy_return_metrics], index=['Portfolio', 'SPY Benchmark'])
    st.table(metrics_df.T)
```

Congratulations you build your own Portfolio Builder! :blush:
