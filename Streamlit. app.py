import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
st.set_page_config(page_title="My Signals App", layout="wide")
st.title("My Signals App")
st.write("Paid Signals - R199 per month")
allowed_codes = ["1234", "7788", "3344", "9021", "5566"]
buyer_names = {"1234":"Test - You", "7788":"Buyer 1", "3344":"Buyer 2", "9021":"Buyer 3", "5566":"Buyer 4"}
password = st.text_input("Enter your own unlock code", type="password")
if password not in allowed_codes:
    st.warning("This app is locked. Pay R199 to get your own unlock code.")
    st.write("Step 1 - Pay with Yoco or Ozow")
    st.write("Step 2 - WhatsApp me your proof of payment")
    st.write("Step 3 - I will send you your own code")
    st.stop()
st.success("Unlocked - Welcome " + buyer_names.get(password, "Buyer"))
timeframe = st.selectbox("Pick Timeframe", ["15m", "1h", "4h", "1d"])
st.write("You picked:", timeframe)
if timeframe == "1d":
    period = "3mo"
else:
    period = "5d"
if st.button("Refresh Signals"):
    symbols = {"EURUSD":"EURUSD=X","GBPUSD":"GBPUSD=X","GOLD":"GC=F","US30":"^DJI","NAS100":"^NDX","US500":"^GSPC","GER40":"^GDAXI","USDJPY":"USDJPY=X"}
    for name, ticker in symbols.items():
        df = yf.download(ticker, period=period, interval=timeframe, progress=False)
        if df.empty:
            continue
        close = df['Close']
        if isinstance(close, pd.DataFrame):
            close = close.iloc[:, 0]
        high = df['High']
        if isinstance(high, pd.DataFrame):
            high = high.iloc[:, 0]
        low = df['Low']
        if isinstance(low, pd.DataFrame):
            low = low.iloc[:, 0]
        openp = df['Open']
        if isinstance(openp, pd.DataFrame):
            openp = openp.iloc[:, 0]
        delta = close.diff()
        gain = delta.clip(lower=0).rolling(14).mean()
        loss = (-delta.clip(upper=0)).rolling(14).mean()
        rsi = 100 - (100 / (1 + (gain / loss)))
        last_rsi = float(rsi.iloc[-1])
        entry = float(close.iloc[-1])
        ema = float(close.ewm(span=50).mean().iloc[-1])
        tr = pd.concat([high-low, (high-close.shift()).abs(), (low-close.shift()).abs()], axis=1).max(axis=1)
        atr = float(tr.rolling(14).mean().iloc[-1])
        if last_rsi < 35:
            signal = "BUY"
        elif last_rsi > 65:
            signal = "SELL"
        elif entry > ema:
            signal = "BUY"
        else:
            signal = "SELL"
        if signal == "BUY":
            sl = entry - atr
            tp = entry + atr + atr
        else:
            sl = entry + atr
            tp = entry - atr - atr
        st.subheader(name + " - " + signal)
        st.write("Timeframe:", timeframe, "Entry:", round(entry,2), "SL:", round(sl,2), "TP:", round(tp,2), "RSI:", round(last_rsi,1))
        fig = go.Figure(data=[go.Candlestick(x=df.index, open=openp, high=high, low=low, close=close)])
        fig.update_layout(title=name + " Candlestick - " + timeframe, xaxis_rangeslider_visible=False, height=400)
        st.plotly_chart(fig, use_container_width=True)
    st.write("Done - Change timeframe and tap Refresh again for new signals")

