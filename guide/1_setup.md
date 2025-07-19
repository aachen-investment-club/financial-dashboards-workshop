
![AIC](../images/aic_banner.png)

# Setup Guide

## System Prerequisites
- You installed ``Python``
- You have set up ``pip`` properly

## Setup

1. Install [git](https://git-scm.com/downloads) on your machine.

2. Install [vscode](https://code.visualstudio.com/) editor.

3. Setup remote access to github (you can skip if you have done this in the past): 
- Create a Github account
- Setup your user name and email (make sure that both match the ones you use on Github)
```sh
git config --global user.name "<your username>"
git config --global user.email "<your email>"
```

4. Clone our GitHub repository with
```sh
git clone https://github.com/aachen-investment-club/financial-dashboards-workshop.git
```

5. Create a virtual environment inside of the project directory: 
```sh
python -m venv venv
```

6. Start the virtual environment with
```sh
.\venv\Scripts\activate #windows 
source venv/bin/activate  #macos
```

7. Install the python requirements with 
```sh
pip install -r requirements.txt
```

8. We recommend to install the following vscode extensions
- git graph
- markdown preview enhanced