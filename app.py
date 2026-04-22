import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px

# 1.Page Setup

st.set_page_config(page_title = "Equity Analaysis Dashboard", layout = "wide")
st.title("Interactive Equity Analysis Dashboard")
st.markdown("Comparing historical perfomrance, volatility, and trading volume of S&P 500 stocks.")

# 2.Sql Extraction and Feature Engineering

#@st.cache_data tells streamslit to remember this data for improve loading

def load_and_engineer_data():
    #Sql Extraction
    conn = sqlite3.connect('stocks.db')
    query = """
        SELECT date, Name as Ticker, open, high, low, close, volume
        FROM historical_prices
    """ 
    df = pd.read_sql(query, conn)
    conn.close()

    #Data Cleaning
    df['date'] = pd.to_datetime(df['date']) #clean dates
    df = df.sort_values(by = ['Ticker', 'date']) #sort for accurate math

    #Engineer new features: 50-day moving Average and Daily Return %

    df['50_MA'] = df.groupby('Ticker')['close'].transform(lambda x: x.rolling(window = 50).mean())
    df['Daily_Return_%'] = df.groupby('Ticker')['close'].pct_change() *100

    return df

#Run function to get data
df = load_and_engineer_data()

# 3.Interactive UI

st.sidebar.header("Filter Options")

#Get a list of all unique stock tickers

available_tickers = df['Ticker'].unique()

#Create a multi-select dropdown (Default is MANGA)

selected_tickers = st.sidebar.multiselect(
    "Select Stocks to Compare:",
    options = available_tickers,
    default=['AAPL', 'MSFT', 'AMZN', 'GOOGL']
)

#Filter the dataframe based on the user's Selection 
filtered_df = df[df['Ticker'].isin(selected_tickers)]


# 4. Business Insights & Visalisations (Plotly)

if not selected_tickers:
    st.warning ("Please select at least one stock from the sidebar.")
else:
    #KPI metrics
    st.subheader("Key Performance Indicatiors (Most recent Data)")
    cols = st.columns(len(selected_tickers))

    for i,ticker in enumerate(selected_tickers):
        ticker_data = filtered_df[filtered_df['Ticker']== ticker]
        latest_close = ticker_data['close'].iloc[-1]
        latest_return = ticker_data['Daily_Return_%'].iloc[-1]

        with cols[i]:
            st.metric(label =f"{ticker} Latest CLose", value = f"${latest_close: .2f}", delta= f"{latest_return:.2f}%")

    st.divider()
#Plotly Charts

col1, col2 = st.columns(2)

with col1:
    st.subheader("Historical Closing Prices")
    fig_price = px.line(filtered_df, x = 'date', y='close', color ='Ticker', title = "Price over Time")
    st.plotly_chart(fig_price, use_container_width= True)
with col2:
    st.subheader("Trading Volume")
    fig_vol = px.bar(filtered_df, x='date', y='volume', color ='Ticker', title="Volume over Time")
    st.plotly_chart(fig_vol, use_container_width= True)

st.subheader("Volatitlity (Daily Returns)")
fig_hist = px.histogram(filtered_df, x='Daily_Return_%', color='Ticker', barmode='overlay', title="Distribution of Daily Returns (Risk)")

st.plotly_chart(fig_hist, use_container_width = True)