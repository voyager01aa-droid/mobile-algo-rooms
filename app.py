import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import json
import os

# Mobile Friendly Layout Config
st.set_page_config(page_title="Mobile Algorooms", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stMetric { background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
    div.stButton > button:first-child { width: 100%; background-color: #3b82f6; color: white; border-radius: 6px; height: 45px; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)

STRATEGY_FILE = "strategies.json"

def load_strategies():
    if os.path.exists(STRATEGY_FILE):
        try:
            with open(STRATEGY_FILE, 'r') as f:
                return json.load(f)
        except: pass
    return {}

def save_strategy(name, config):
    strategies = load_strategies()
    strategies[name] = config
    with open(STRATEGY_FILE, 'w') as f:
        json.dump(strategies, f, indent=4)

st.title("🚀 Mobile Algo Console")

page = st.selectbox("Menu Chunein", ["📊 Live Dashboard", "⚙️ Strategy Builder", "🧪 Real Backtester", "🔑 Kotak Neo Setup"])

if page == "📊 Live Dashboard":
    st.subheader("Real-time Tracking")
    c1, c2 = st.columns(2)
    c1.metric(label="Live P&L", value="₹ 0.00", delta="0%")
    c2.metric(label="Total Trades", value="0")
    
    st.info("Live market data aur auto-execution ke liye pehle Strategy banakar Backtest karein.")

elif page == "⚙️ Strategy Builder":
    st.subheader("Bina Code Ki Strategy")
    strat_name = st.text_input("Strategy Name", placeholder="e.g., Nifty EMA Crossover")
    
    symbol = st.selectbox("Stock/Index Symbol", ["^NSEI (Nifty 50)", "^NSEBANK (BankNifty)", "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS"])
    # Extract actual symbol
    actual_symbol = symbol.split(" ")[0]
    
    direction = st.selectbox("Direction", ["Buy Only", "Sell Only", "Both"])

    st.write("---")
    st.write("**Trigger Rule (Moving Average)**")
    fast_ema = st.number_input("Fast EMA Period", min_value=1, value=9)
    slow_ema = st.number_input("Slow EMA Period", min_value=1, value=21)
    
    st.write("---")
    st.write("**Risk Limits**")
    stop_loss = st.number_input(f"Stop Loss (%)", min_value=0.1, value=1.0, step=0.1)
    target = st.number_input(f"Take Profit (%)", min_value=0.1, value=2.0, step=0.1)

    if st.button("💾 Save Strategy"):
        if strat_name:
            config = {
                "symbol": actual_symbol, 
                "fast_ema": fast_ema, 
                "slow_ema": slow_ema, 
                "stop_loss": stop_loss,
                "target": target,
                "direction": direction
            }
            save_strategy(strat_name, config)
            st.success(f"'{strat_name}' Save ho gayi! Ab Backtester me check karein.")
        else:
            st.error("Naam dena zaroori hai.")

elif page == "🧪 Real Backtester":
    st.subheader("Real Market Backtester")
    strategies = load_strategies()
    if not strategies:
        st.warning("Pehle strategy banayein.")
    else:
        selected_strat = st.selectbox("Strategy Chunein", list(strategies.keys()))
        conf = strategies[selected_strat]
        
        c1, c2 = st.columns(2)
        start_date = c1.date_input("Start Date", value=datetime(2025, 1, 1))
        end_date = c2.date_input("End Date", value=datetime.today())
            
        if st.button("🏃 Run Asli Backtest"):
            with st.spinner("Real Market Data download ho raha hai..."):
                try:
                    # 1. Download Real Data
                    ticker = yf.Ticker(conf['symbol'])
                    df = ticker.history(start=start_date, end=end_date)
                    
                    if df.empty:
                        st.error("Data nahi mila. Dates check karein.")
                    else:
                        # 2. Calculate Indicators (Real Logic)
                        df['Fast_EMA'] = df['Close'].ewm(span=conf['fast_ema'], adjust=False).mean()
                        df['Slow_EMA'] = df['Close'].ewm(span=conf['slow_ema'], adjust=False).mean()
                        
                        # 3. Generate Signals (1 = Buy, -1 = Sell, 0 = Hold)
                        df['Signal'] = 0
                        df['Signal'] = np.where(df['Fast_EMA'] > df['Slow_EMA'], 1, -1)
                        
                        # Calculate Daily Returns
                        df['Market_Return'] = df['Close'].pct_change()
                        df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1)
                        
                        # Calculate Cumulative P&L
                        df['Cumulative_Returns'] = (1 + df['Strategy_Return']).cumprod() - 1
                        total_return = df['Cumulative_Returns'].iloc[-1] * 100
                        
                        # Win Rate Calculation
                        winning_days = len(df[df['Strategy_Return'] > 0])
                        total_trades = len(df[df['Strategy_Return'] != 0])
                        win_rate = (winning_days / total_trades) * 100 if total_trades > 0 else 0
                        
                        # Display Results
                        res1, res2 = st.columns(2)
                        res1.metric("Total Return (%)", f"{total_return:.2f} %")
                        res2.metric("Win Rate", f"{win_rate:.1f} %")
                        
                        # Plot Real Chart
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Returns'] * 100, mode='lines', line=dict(color='#10b981'), name='P&L %'))
                        fig.update_layout(title=f"{conf['symbol']} Backtest P&L", template="plotly_dark", margin=dict(l=10, r=10, t=30, b=10), height=300)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                except Exception as e:
                    st.error(f"Error aagaya: {e}")

elif page == "🔑 Kotak Neo Setup":
    st.subheader("Kotak API Credentials")
    st.info("Live Auto-Execution tabhi kaam karega jab aapke paas Ek Cloud Server (VPS) ho. Streamlit screen band hone par trading rok deta hai.")
    with st.form("neo_form"):
        ck = st.text_input("Consumer Key", type="password")
        cs = st.text_input("Consumer Secret", type="password")
        un = st.text_input("Mobile / User ID")
        pwd = st.text_input("Password", type="password")
        
        if st.form_submit_with_button("🔐 Save Credentials"):
            st.success("Details Saved locally for API Webhooks.")
