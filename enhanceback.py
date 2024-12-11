import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go

# App Title
st.title("Interactive Backtesting Engine")

# Sidebar Options
st.sidebar.header("Configuration")
timeframe = st.sidebar.selectbox("Select Timeframe", ["Daily", "Weekly", "Monthly"])
strategy = st.sidebar.selectbox(
    "Select Strategy",
    ["MACD", "Moving Average", "RSI", "VWAP", "Bollinger Bands"]
)
investment_style = st.sidebar.selectbox(
    "Select Investment Style", ["Aggressive", "Moderate", "Passive"]
)

# File Upload
uploaded_file = st.file_uploader("Upload CSV File (e.g., Reliance Shares)", type="csv")

if uploaded_file:
    data = pd.read_csv(uploaded_file)
else:
    # Load default data for debugging
    st.info("No file uploaded. Using default data for demo.")
    dates = pd.date_range(start="2023-01-01", periods=100)
    prices = np.cumsum(np.random.randn(100)) + 100
    data = pd.DataFrame({"Date": dates, "Close": prices})

# Ensure required columns
if "Date" in data.columns and "Close" in data.columns:
    data["Date"] = pd.to_datetime(data["Date"])
    data.set_index("Date", inplace=True)

    st.subheader("Stock Data Visualization")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price"))
    fig.update_layout(title="Stock Price Over Time", xaxis_title="Date", yaxis_title="Price")
    st.plotly_chart(fig)

    # Bollinger Bands Strategy
    if strategy == "Bollinger Bands":
        st.subheader("Bollinger Bands Strategy")
        period = st.sidebar.slider("Bollinger Band Period", min_value=5, max_value=100, value=20)
        std_dev = st.sidebar.slider("Standard Deviation", min_value=1, max_value=3, value=2)

        data["SMA"] = data["Close"].rolling(window=period).mean()
        data["Upper Band"] = data["SMA"] + (std_dev * data["Close"].rolling(window=period).std())
        data["Lower Band"] = data["SMA"] - (std_dev * data["Close"].rolling(window=period).std())

        # Generate buy/sell signals
        data["Buy Signal"] = np.where(data["Close"] < data["Lower Band"], data["Close"], np.nan)
        data["Sell Signal"] = np.where(data["Close"] > data["Upper Band"], data["Close"], np.nan)

        # Plot Bollinger Bands and Signals
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data["Upper Band"], mode="lines", name="Upper Band", line=dict(color="red", dash="dash")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Lower Band"], mode="lines", name="Lower Band", line=dict(color="green", dash="dash")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Buy Signal"], mode="markers", name="Buy Signal", marker=dict(color="green", size=10, symbol="triangle-up")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Sell Signal"], mode="markers", name="Sell Signal", marker=dict(color="red", size=10, symbol="triangle-down")))
        fig.update_layout(title="Bollinger Bands with Buy/Sell Signals", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig)

    # MACD Strategy
    elif strategy == "MACD":
        st.subheader("MACD Strategy")
        short_window = st.sidebar.slider("Short Window", min_value=5, max_value=50, value=12)
        long_window = st.sidebar.slider("Long Window", min_value=20, max_value=200, value=26)
        signal_window = st.sidebar.slider("Signal Window", min_value=5, max_value=50, value=9)

        data["MACD"] = data["Close"].ewm(span=short_window, adjust=False).mean() - data["Close"].ewm(span=long_window, adjust=False).mean()
        data["Signal"] = data["MACD"].ewm(span=signal_window, adjust=False).mean()

        # Generate buy/sell signals
        data["Buy Signal"] = np.where((data["MACD"] > data["Signal"]) & (data["MACD"].shift(1) <= data["Signal"].shift(1)), data["Close"], np.nan)
        data["Sell Signal"] = np.where((data["MACD"] < data["Signal"]) & (data["MACD"].shift(1) >= data["Signal"].shift(1)), data["Close"], np.nan)

        # Plot MACD and Signals
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["MACD"], mode="lines", name="MACD", line=dict(color="blue")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Signal"], mode="lines", name="Signal Line", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Buy Signal"], mode="markers", name="Buy Signal", marker=dict(color="green", size=10, symbol="triangle-up")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Sell Signal"], mode="markers", name="Sell Signal", marker=dict(color="red", size=10, symbol="triangle-down")))
        fig.update_layout(title="MACD with Buy/Sell Signals", xaxis_title="Date", yaxis_title="Value")
        st.plotly_chart(fig)

    # Moving Average Strategy
    elif strategy == "Moving Average":
        st.subheader("Moving Average Strategy")
        ma_period = st.sidebar.slider("Moving Average Period", min_value=5, max_value=100, value=20)

        data["MA"] = data["Close"].rolling(window=ma_period).mean()

        # Generate buy/sell signals
        data["Buy Signal"] = np.where((data["Close"] > data["MA"]) & (data["Close"].shift(1) <= data["MA"].shift(1)), data["Close"], np.nan)
        data["Sell Signal"] = np.where((data["Close"] < data["MA"]) & (data["Close"].shift(1) >= data["MA"].shift(1)), data["Close"], np.nan)

        # Plot Moving Average and Signals
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["Close"], mode="lines", name="Close Price"))
        fig.add_trace(go.Scatter(x=data.index, y=data["MA"], mode="lines", name="Moving Average", line=dict(color="orange")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Buy Signal"], mode="markers", name="Buy Signal", marker=dict(color="green", size=10, symbol="triangle-up")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Sell Signal"], mode="markers", name="Sell Signal", marker=dict(color="red", size=10, symbol="triangle-down")))
        fig.update_layout(title="Moving Average with Buy/Sell Signals", xaxis_title="Date", yaxis_title="Price")
        st.plotly_chart(fig)

    # RSI Strategy
    elif strategy == "RSI":
        st.subheader("RSI Strategy")
        rsi_period = st.sidebar.slider("RSI Period", min_value=5, max_value=50, value=14)
        overbought = st.sidebar.slider("Overbought Level", min_value=50, max_value=90, value=70)
        oversold = st.sidebar.slider("Oversold Level", min_value=10, max_value=50, value=30)

        delta = data["Close"].diff()
        gain = np.where(delta > 0, delta, 0)
        loss = np.where(delta < 0, -delta, 0)
        avg_gain = pd.Series(gain).rolling(window=rsi_period).mean()
        avg_loss = pd.Series(loss).rolling(window=rsi_period).mean()
        rs = avg_gain / avg_loss
        data["RSI"] = 100 - (100 / (1 + rs))

        # Generate buy/sell signals
        data["Buy Signal"] = np.where(data["RSI"] < oversold, data["Close"], np.nan)
        data["Sell Signal"] = np.where(data["RSI"] > overbought, data["Close"], np.nan)

        # Plot RSI and Signals
        fig = go.Figure()
        fig.add_trace(go.Scatter(x=data.index, y=data["RSI"], mode="lines", name="RSI", line=dict(color="blue")))
        fig.add_hline(y=overbought, line=dict(color="red", dash="dash"), name="Overbought")
        fig.add_hline(y=oversold, line=dict(color="green", dash="dash"), name="Oversold")
        fig.add_trace(go.Scatter(x=data.index, y=data["Buy Signal"], mode="markers", name="Buy Signal", marker=dict(color="green", size=10, symbol="triangle-up")))
        fig.add_trace(go.Scatter(x=data.index, y=data["Sell Signal"], mode="markers", name="Sell Signal", marker=dict(color="red", size=10, symbol="triangle-down")))
        fig.update_layout(title="RSI with Buy/Sell Signals", xaxis_title="Date", yaxis_title="RSI")
        st.plotly_chart(fig)

    # VWAP Strategy
    elif strategy == "VWAP":
        st.subheader("VWAP Strategy")
        data["VWAP"] = (data["Close"] * data.index).cumsum() / data.index.cumsum()
        st.write("VWAP integration logic...")
else:
    st.error("CSV must contain 'Date' and 'Close' columns.")
