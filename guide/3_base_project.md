![AIC](../images/aic_banner.png)

# Base Project

## Sharing your code with others
So, it is finally time to merge your base projects. Assuming you have a group of at least two people, decide whose dashboards you would like to use from now on. All of you will be using this dashboard as a basis. Do the following: 

0. Owner: Dont forget to run `git add .` and `git commit`!   
1. The owner of the selected version must push their code to GitHub. 
```sh 
git push -u origin <your-branch-name>
```
Note that when doing this for the first time, i.e. when the branch has not been backed up with Github, this command is necessary. After this, you can simply use `git push`.
2. Now, your collaborators can download your code. For this, they need to run: 
```sh
git fetch origin
git checkout <owner-branch-name>
git pull origin <owner-branch-name> 
```
this is also necessary when pulling a branch for the first time. After the first time, it is enough to run `git pull` to synchronize with the current stand. Note that running `git pull` **might lead** to conflicts, hence resolution might be necessary!

## Workflow when working with others
One last thing, before you start working on your own: there exists a typical workflow when working with others. Here we assume that you and your collaborators have a copy of the same branch in your respective local machines. Here we list a few important standards/ good practices:  

First of all, *BEFORE WRITING ANY CODE* always run `git pull`. This way you ensure to have the latest version of the code and avoid conflict resolution. 

After you are done writing your code, and fully sure it works as intended, run the usual commands to sync with the remote repo:  
```sh
git add . 
git commit -m "some descriptive message summarizing your changes" 
git push
```

Never develop (code) in the main branch. The main branch represents the stable version of your code, therefore, only add new features to it once you are fully sure everything works. Therefore, always create a development branch for your new feature, then test it online, and then, once you are sure, merge with main.


## pull requests

![pull request](../images/pull_request.webp)
If you should never code in main,... how do you merge main with a development branch in my *REMOTE* repository? For this you use *pull requests*. Whenever github sees that `main` is outdated with respect to other online branches, it will prompt you to do a pull request. The workflow is the following: 
1. first, you create the pull request, indicating to the repositor owner that you "feel ready to merge with main"
2. the admins/repo owners will then look at your code, and hopefully, merge with main.


# Dashboards

From this section on, we will focus on dashboard creation. You will first start working on three small projects: 
1. A stock viewer that allows you to pick specific stocks from the S&P500 and graph them. 
2. A portfolio builder, which you can use to simulate some stock trades.
3. (optional) If you feel that the two previous tasks were to simple, we have a challenge for you! **pending**



## Stock viewer

Go to the file `./pages/Stock Viewer.py`. You will be working here for the rest of this task.

We already took care of creating a dataset for you. The `load_data` function was implemented for this, which is import at the top of the file. 

Make sure to always: 
1. paste a single code block.
2. read the code, try to understand it.
2. save your file.
3. check your website and try to spot the changes; associate them with your code.

First, name the site: 
```py
st.set_page_config(page_title="Stock Viewer")
st.title("📈 S&P 500 Stocks Viewer")
st.write("Select a stock ticker from the list to view its price history.")
```
Next, load the data and create a select box. This component
will list out all the available stocks in the S&P500, and 
let you choose one of them for posterior visualization.

The tickers contain the data corresponding to each stock. 
```py
# Load data
df = load_data()

# Display all available tickers (i.e. DataFrame columns)
all_tickers = df.columns.tolist()

# Create scrollable list of tickers
selected_ticker = st.selectbox(
    "Choose a stock ticker",
    all_tickers,
    index=all_tickers.index("AAPL.OQ") if "AAPL.OQ" in all_tickers else 0,
)
```
Next, we do a preprocessing step: we filter the data such that we only have the selected ticker remaining: 
```py
# Filter data for selected ticker
df_selected = df[[selected_ticker]].copy().dropna()
```

Finally, lets create a line plot! You can do this using: 
```py
fig = px.line(
    df_selected,
    title=f"{selected_ticker} Stock Price",
    labels={"value": "Close Price (USD)", "Date": "Date"},
)

# Update each axis label
fig.update_layout(
    xaxis_title="Date",
    yaxis_title="Close Price (USD)",
)
```
Finally, you can insert the chart in your site: 
```py
# Show plot
st.plotly_chart(fig, use_container_width=True)
```
Nicely done! If everything worked properly, you should have a working S&P50 stock viewer. Make sure to play around with it, before proceeding ;). 
## Portfolio Builder
Next, we proceed with a portfolio builder.

Again, start by naming your subpage: 
```py
# ----------------------------
# Page Setup
st.set_page_config(page_title="Portfolio Builder")
st.title("📊 Portfolio Builder")
st.write("Select tickers, assign weights, and visualize your portfolio performance.")
```
Now, load the data and get all ticker names (i.e. all stock tickers). 
```py
# ----------------------------
# Load Data
df = load_data()
all_tickers = df.columns.tolist()
```
Insert a **multiselect** component that allows you to select at least one stock. Note that this returns a list!
```py
# ----------------------------
# Portfolio Construction
st.header("Select Tickers")

selected_tickers = st.multiselect(
    "Choose the tickers you want in your portfolio:",
    all_tickers,
    default=["AAPL.OQ"] if "AAPL.OQ" in all_tickers else []
)
```
Next, we create a component to select the weights that you will assign to each stock:
```py
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
else:
    st.info("Please select at least one ticker to begin building your portfolio.")
```
Now, we would like to plot our portfolio's performance. 
Still inside the inside if statement from the last block, paste the following (the outer-most if statement): 
```py
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
```
We can also get some more information about our holding period. 
Past the following within the same if statement as in the last step:
```py
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
```
How about some risk metrics? Lets evaluate the performance
 of you picks! For this, first we calculate them: (paste 
 them inside of the same if statement from before)
```py

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
```
Now, lets visualize them! We can plot our daily returns
in a Bar chart, and our risk metrics in a tabular fashion. 
Again, paste the following lines of codes inside the if statement from before: 
```py

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
```


## Challenge 
