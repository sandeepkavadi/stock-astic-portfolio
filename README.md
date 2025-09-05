# Stock-astic Portfolio

## Description
This application is designed to track stock market data, identify potential trade opportunities, and help manage overall portfolio health by considering risk-return tradeoffs. It aims to provide trade recommendations from both short-term and long-term perspectives. A key feature is its ability to connect to a Schwab account via API for fetching data and, eventually, executing trades after user confirmation.

## Features Implemented

### 1. Data Acquisition
- **Primary Source:** Alpha Vantage API for daily stock market data.
- **Fallback Source:** Seamless fallback to `yfinance` for data fetching if Alpha Vantage API calls fail (e.g., due to rate limits or errors).
- **Caching:** Implemented a local file-based caching mechanism to store fetched stock data, reducing redundant API calls and improving performance.

### 2. Technical Analysis
- **Comprehensive Indicators:** Calculates a range of technical indicators essential for market analysis:
    - **Simple Moving Average (SMA):** For identifying trends.
    - **Exponential Moving Average (EMA):** Giving more weight to recent prices.
    - **Relative Strength Index (RSI):** To identify overbought/oversold conditions.
    - **Moving Average Convergence Divergence (MACD):** A trend-following momentum indicator.
    - **Bollinger Bands:** To measure market volatility and identify potential price reversals.
    - **Stochastic Oscillator:** Compares a stock's closing price to its price range over a given period to identify momentum.

### 3. Trading Strategies
- **Signal Generation:** Implemented various trading strategies to generate buy and sell signals based on technical indicator crossovers and thresholds:
    - **SMA Crossover Strategy:** Buy/sell signals based on short-term vs. long-term SMA crossovers.
    - **RSI Strategy:** Buy/sell signals based on RSI crossing overbought/oversold levels.
    - **MACD Crossover Strategy:** Buy/sell signals based on MACD line crossing its signal line.
    - **Bollinger Bands Strategy:** Buy/sell signals based on price interacting with upper and lower Bollinger Bands.
    - **Stochastic Oscillator Strategy:** Buy/sell signals based on %K and %D line crossovers and overbought/oversold levels.

### 4. Portfolio Management
- **Schwab API Integration:** Connects to the Schwab Developer API to fetch real-time portfolio positions.
- **Portfolio Overview:** Displays current stock holdings and calculates the total market value of the portfolio.

### 5. Interactive Dashboard (Built with Dash and Plotly)
- **Watchlist Tab:**
    - **Stock Selection:** Allows users to select stocks from a dropdown populated with their custom watchlist and portfolio holdings.
    - **Watchlist Management:** Functionality to add and remove stock symbols from a persistent watchlist file (`watchlist.txt`).
    - **Symbol Validation:** Validates new stock symbols against Alpha Vantage/yfinance to ensure they are legitimate.
    - **Interactive Charts:** Displays candlestick charts with overlaid technical indicators (SMA, EMA, Bollinger Bands, RSI, MACD, Stochastic Oscillator) and visual buy/sell signals from implemented strategies.
- **Portfolio Performance Tab:**
    - Displays a table of current stock positions fetched from the Schwab API.
    - Shows the total market value of the portfolio.

## Technology Stack
- **Backend/Logic:** Python 3.x
- **Web Framework:** Dash
- **Charting:** Plotly Graph Objects
- **Data Manipulation:** Pandas
- **API Interaction:** `requests`, `yfinance`, `schwab-py`
- **Authentication:** OAuth 2.0 flow for Schwab API

## Future Enhancements
- Implement more sophisticated combination trading strategies.
- Calculate detailed profit/loss and other portfolio health metrics (requires cost basis data).
- Integrate Schwab API for programmatic trade execution (with user confirmation).
- Deployment to AWS using the free tier.

## Setup and Running
1.  **Clone the repository:**
    `git clone <repository_url>`
    `cd stock-astic-portfolio`
2.  **Install dependencies:**
    `pip install -r requirements.txt`
3.  **Alpha Vantage API Key:**
    - Obtain a free API key from [Alpha Vantage](https://www.alphavantage.co/).
    - Create a file named `.ALPHA_VANTAGE_KEY.txt` in the project root and paste your API key into it.
4.  **Schwab API Authentication:**
    - Obtain API key, app secret, and set up a redirect URI (e.g., `https://127.0.0.1`) from the Schwab Developer Portal.
    - Ensure you have Google Chrome and the correct `chromedriver` installed and in your system's PATH.
    - Run the authentication script:
        `python3 scripts/authenticate_schwab.py`
    - Follow the prompts to log in and authorize. Your Schwab credentials will be saved to `schwab_config.json`.
5.  **Run the application:**
    `python3 -m src.dashboard.app`
    Open the URL displayed in your terminal (e.g., `http://127.0.0.1:8050/`) in your web browser.
