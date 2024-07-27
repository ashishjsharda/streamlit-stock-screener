import yfinance as yf
import pandas as pd
from bs4 import BeautifulSoup
import requests
import streamlit as st


# Fetch stock data
def fetch_stock_data(ticker):
    stock = yf.Ticker(ticker)
    data = stock.history(period="ytd")  # Get year-to-date data for 2024
    return data


# Fetch market cap
def fetch_market_cap(ticker):
    stock = yf.Ticker(ticker)
    info = stock.info
    return info.get('marketCap', 0)


# Fetch news
def fetch_news(ticker):
    url = f"https://finance.yahoo.com/quote/{ticker}?p={ticker}&.tsrc=fin-srch"
    response = requests.get(url)
    soup = BeautifulSoup(response.text, "html.parser")
    headlines = soup.find_all('h3', class_='Mb(5px)')
    news = [headline.text for headline in headlines]
    return news[:5]  # Return top 5 news articles


# Filter stocks
def filter_stocks(stock_data, market_cap, min_market_cap, max_market_cap, min_volume, max_volatility):
    filtered_data = stock_data.copy()
    filtered_data['Market Cap'] = market_cap

    if market_cap < min_market_cap or market_cap > max_market_cap:
        return pd.DataFrame()  # Return empty DataFrame if market cap doesn't match criteria

    # Momentum (simple example: recent price trend)
    filtered_data['Momentum'] = filtered_data['Close'].pct_change().rolling(window=5).mean()

    # Daily shares traded (volume)
    filtered_data = filtered_data[filtered_data['Volume'] > min_volume]

    # Volatility (standard deviation of returns)
    filtered_data['Volatility'] = filtered_data['Close'].pct_change().rolling(window=10).std()
    filtered_data = filtered_data[filtered_data['Volatility'] < max_volatility]

    return filtered_data


# Streamlit UI
st.title('Tech Companies Stock Screener')

ticker = st.text_input('Enter Stock Ticker', value='AAPL')
min_market_cap = st.number_input('Minimum Market Cap (in billions)', value=100.0)
max_market_cap = st.number_input('Maximum Market Cap (in billions)', value=1000.0)
min_volume = st.number_input('Minimum Daily Volume (in millions)', value=1)
max_volatility = st.number_input('Maximum Volatility (standard deviation of returns)', value=0.02)

if st.button('Screen'):
    try:
        stock_data = fetch_stock_data(ticker)
        st.write("Fetched Stock Data:")
        st.write(stock_data.head())  # Display the fetched stock data

        market_cap = fetch_market_cap(ticker)
        st.write(f"Market Cap: {market_cap}")

        filtered_data = filter_stocks(stock_data, market_cap, min_market_cap * 1e9, max_market_cap * 1e9,
                                      min_volume * 1e6, max_volatility)

        if filtered_data.empty:
            st.write("No stocks matched your criteria.")
        else:
            st.write("Filtered Stock Data")
            st.write(filtered_data)

        st.write("Recent News")
        news = fetch_news(ticker)
        for article in news:
            st.write(article)
    except Exception as e:
        st.write("An error occurred while fetching data. Please ensure the ticker symbol is correct.")
        st.write(str(e))
