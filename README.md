# StockJockey
A light-weight Flask app to analyze and score stocks to simplify and speed up trade decisions

## Overview
StockJockey is an application for rating stocks (and eventually other securities) based on historical
data. The rating is based on the Nasdaq Dozen analysis method and provide a score from 1 (worst) to
12 (best).

The app originated as a Google Apps Script project to augment a Google Sheet and is now being built
from the ground up as a Flask app.

## Installation
To run locally:  
(requires python and pip)  
1. Install the app as a package: `pip install git+https://github.com/indierambler/stockjockey.git`
2. Serve the flask app locally: `flask --app stockjockey run`

## Future Updates
- Track and graph historical scores for stocks
- Automatically retrieve and score closest competitor stocks

