import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import db
from data_fetcher import fetch_stock_data, add_technical_indicators

# Configure the page
st.set_page_config(page_title="Nifty 500 EOD Analyser", layout="wide")

# Initialize Database and session state on first load
if "db_initialized" not in st.session_state:
    db.init_db()
    st.session_state.db_initialized = True

# Custom CSS for a better look
st.markdown("""
<style>
    .reportview-container {
        background: #f0f2f6
    }
    .main {
        background-color: #ffffff;
        padding: 2rem;
        border-radius: 10px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
    }
    h1 {
        color: #1f77b4;
    }
</style>
""", unsafe_allow_html=True)


st.title("📈 Nifty 500 EOD Stock Analyser")

# --- Authentication ---
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

import auth

if not st.session_state.authenticated:
    st.sidebar.subheader("Login / Signup")
    
    auth_mode = st.sidebar.radio("Choose Mode", ["Login", "Sign Up"])
    email = st.sidebar.text_input("Email")
    password = st.sidebar.text_input("Password", type="password")
    
    if st.sidebar.button(auth_mode):
        if not email or not password:
            st.sidebar.error("Please enter email and password.")
        else:
            if auth_mode == "Login":
                success, result = auth.sign_in(email, password)
            else:
                success, result = auth.sign_up(email, password)
                
            if success:
                st.session_state.authenticated = True
                st.sidebar.success(f"Successfully {auth_mode.lower()}ed!")
                st.rerun()
            else:
                st.sidebar.error(result)
                
    st.stop()
else:
    if st.sidebar.button("Logout"):
        st.session_state.authenticated = False
        st.rerun()

# --- Main Dashboard ---
st.sidebar.header("Configuration")

# Fetch stocks from database
stocks_list = db.get_all_stocks()
if not stocks_list:
    st.warning("No stocks found in the database. Please click below to load the stock list.")
    if st.button("Load Nifty 500 Data"):
        with st.spinner("Fetching data from NSE..."):
            db.load_nifty500_to_db()
            st.rerun()
    st.stop()

# Format options for selectbox
stock_options = {f"{symbol} - {name}": symbol for symbol, name in stocks_list}
selected_stock_label = st.sidebar.selectbox("Select a Stock", options=list(stock_options.keys()))
selected_symbol = stock_options[selected_stock_label]

period = st.sidebar.selectbox("Select Period", options=["1mo", "3mo", "6mo", "1y", "2y", "5y", "max"], index=3)

st.subheader(f"Analysis for {selected_stock_label}")

with st.spinner(f"Fetching historical data for {selected_symbol}..."):
    df = fetch_stock_data(selected_symbol, period=period)
    
if df.empty:
    st.error(f"Failed to fetch data for {selected_symbol}. It might be delisted or the symbol is incorrect.")
else:
    # Add indicators
    df = add_technical_indicators(df)
    
    # Key Metrics
    latest_close = df['Close'].iloc[-1]
    prev_close = df['Close'].iloc[-2]
    change = latest_close - prev_close
    pct_change = (change / prev_close) * 100
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Latest Close", f"₹{latest_close:.2f}", f"{change:.2f} ({pct_change:.2f}%)")
    col2.metric("Volume", f"{int(df['Volume'].iloc[-1]):,}")
    
    if 'RSI' in df.columns:
        col3.metric("RSI (14)", f"{df['RSI'].iloc[-1]:.2f}")
    if 'MACD' in df.columns:
        col4.metric("MACD", f"{df['MACD'].iloc[-1]:.2f}")

    # --- Plotly Charts ---
    st.markdown("### Price & Moving Averages")
    
    # 1. Price Chart (Candlestick + MAs)
    fig_price = go.Figure()
    fig_price.add_trace(go.Candlestick(x=df.index,
                                       open=df['Open'],
                                       high=df['High'],
                                       low=df['Low'],
                                       close=df['Close'],
                                       name='Price'))
    if 'SMA_20' in df.columns:
        fig_price.add_trace(go.Scatter(x=df.index, y=df['SMA_20'], line=dict(color='orange', width=1.5), name='SMA 20'))
    if 'SMA_50' in df.columns:
        fig_price.add_trace(go.Scatter(x=df.index, y=df['SMA_50'], line=dict(color='blue', width=1.5), name='SMA 50'))
        
    fig_price.update_layout(height=500, xaxis_rangeslider_visible=False, template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_price, use_container_width=True)

    # 2. Volume Chart
    st.markdown("### Volume")
    fig_vol = go.Figure()
    colors = ['green' if row['Open'] - row['Close'] <= 0 else 'red' for index, row in df.iterrows()]
    fig_vol.add_trace(go.Bar(x=df.index, y=df['Volume'], marker_color=colors, name='Volume'))
    fig_vol.update_layout(height=300, template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
    st.plotly_chart(fig_vol, use_container_width=True)

    # 3. RSI Chart
    if 'RSI' in df.columns:
        st.markdown("### Relative Strength Index (RSI)")
        fig_rsi = go.Figure()
        fig_rsi.add_trace(go.Scatter(x=df.index, y=df['RSI'], line=dict(color='purple', width=1.5), name='RSI'))
        fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
        fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
        fig_rsi.update_layout(height=300, template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_rsi, use_container_width=True)

    # 4. MACD Chart
    if 'MACD' in df.columns:
        st.markdown("### MACD")
        fig_macd = go.Figure()
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD'], line=dict(color='blue', width=1.5), name='MACD Line'))
        fig_macd.add_trace(go.Scatter(x=df.index, y=df['MACD_Signal'], line=dict(color='orange', width=1.5), name='Signal Line'))
        fig_macd.add_trace(go.Bar(x=df.index, y=df['MACD_Diff'], marker_color=['green' if val > 0 else 'red' for val in df['MACD_Diff']], name='MACD Histogram'))
        fig_macd.update_layout(height=300, template="plotly_white", margin=dict(l=20, r=20, t=20, b=20))
        st.plotly_chart(fig_macd, use_container_width=True)

    # Raw Data Expander
    with st.expander("View Raw Data"):
        st.dataframe(df.tail(100).sort_index(ascending=False))
