![AIC](../images/aic_banner.png)

# 4) Team Project


## Build Teams and merge your Base Projects
It's time to build teams and merge your base projects with others. Assuming you have a group of at least three people, decide whose dashboards you would like to use from now on. Now you will merge your branches into one. Do the following: 

0. Owner: Don't forget to run `git add .` and `git commit`!   
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


## Pull requests

![pull request](../images/pull_request.webp)
If you should never code in main,... how do you merge main with a development branch in my *REMOTE* repository? For this you use *pull requests*. Whenever github sees that `main` is outdated with respect to other online branches, it will prompt you to do a pull request. The workflow is the following: 
1. first, you create the pull request, indicating to the repositor owner that you "feel ready to merge with main"
2. the admins/repo owners will then look at your code, and hopefully, merge with main.

## Dashboard Ideas

### Rule based Rebalancing for Portfolio

### Leveraged ETFs

### Market Stress Indicator
- Rolling volatility / Momentum Based
- Volatility Targeting: Rebalance portfolio to reach a target volatility

### Pairs Trading
- Find pairs of stocks that behave similar e.g. by conintegration test
- Trade the spread between these two
- More advanced: instead of single stocks find baskets that behave similar

### Index Arbitrage with Market Factor Basket
- I don't know if this works
- Compute principal eigenvector of covariance matrix between each stock
- Use weights as market factor portfolio to trade against the SPY

### Model example derivatives
- Variance Swap, Barrier Options, Black Scholes

### Industry Factor Model