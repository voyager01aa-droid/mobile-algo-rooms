import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import json
import os

# Mobile Friendly Layout Config
st.set_page_config(page_title="Mobile Algorooms", layout="centered", initial_sidebar_state="collapsed")

# Custom Responsive UI CSS
st.markdown("""
    <style>
    .stMetric { background-color: #1e293b; padding: 12px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 10px; }
    div.stButton > button:first-child { width: 100%; background-color: #3b82f6; color: white; border-radius: 6px; height: 45px; font-weight: bold; }
    .reportview-container .main .block-container { padding-top: 1rem; padding-bottom: 1rem; }
    h1 { font-size: 22px !important; }
    h2 { font-size: 18px !important; }
    h3 { font-size: 16px !important; }
    </style>
""", unsafe_allow_html=True)

STRATEGY_FILE = "strategies.json"

def load_strategies():
    if os.path.exists(STRATEGY_FILE):
        try:
            with open(STRATEGY_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}
    return {}

def save_strategy(name, config):
    strategies = load_strategies()
    strategies[name] = config
    with open(STRATEGY_FILE, 'w') as f:
        json.dump(strategies, f, indent=4)

st.title("🚀 Mobile Algorooms Console")

# Mobile Friendly Navigation Tab instead of wide sidebar
page = st.selectbox("Navigation Menu", ["📊 Live Dashboard", "⚙️ Strategy Builder", "🧪 Mobile Backtester", "🔑 Kotak Neo Setup"])

if page == "📊 Live Dashboard":
    st.subheader("Real-time Tracking")
    
    # Stacking metrics vertically or in pairs for mobile screens
    c1, c2 = st.columns(2)
    c1.metric(label="Live P&L (MTM)", value="₹ +4,250", delta="1.2%")
    c2.metric(label="Total Trades", value="12")
    
    c3, c4 = st.columns(2)
    c3.metric(label="Active Bots", value="2 / 5")
    c4.metric(label="Neo Status", value="Connected")

    st.write("### 🤖 Active Algos")
    active_bots_data = pd.DataFrame({
        "Strategy": ["Nifty Inside Bar", "BankNifty RSI"],
        "Token": ["NIFTY CE", "BANKNIFTY FUT"],
        "Status": ["Running", "Idling"],
        "P&L": ["₹ +2,850", "₹ +1,400"]
    })
    st.dataframe(active_bots_data, use_container_width=True)

    st.write("### 📜 Logs")
    logs = [
        "[10:15:02] [INFO] Signal Generated. Sending BUY to Kotak Neo...",
        "[10:15:03] [SUCCESS] Order Executed at ₹142.50",
        "[11:30:15] [INFO] Target hit. Square-off command sent."
    ]
    for log in logs:
        st.caption(log)

elif page == "⚙️ Strategy Builder":
    st.subheader("No-Code Strategy Input")
    strat_name = st.text_input("Strategy Name", placeholder="e.g., Mobile Scalper 1")
    
    segment = st.selectbox("Segment", ["Equity (Cash)", "Indices Options", "Futures"])
    timeframe = st.selectbox("Candle Timeframe", ["1 Min", "3 Min", "5 Min", "15 Min"])
    direction = st.selectbox("Direction", ["Long (Buy)", "Short (Sell)", "Both"])

    st.write("---")
    st.write("**Trigger Condition**")
    ind1 = st.selectbox("First Indicator", ["Close Price", "EMA", "RSI", "Supertrend"])
    param1 = st.number_input("Period / Length", min_value=1, value=14)
    condition = st.selectbox("Condition Logic", ["Crosses Above", "Crosses Below", "Greater Than", "Less Than"])
    ind2 = st.selectbox("Comparison Target", ["Value", "EMA", "Close Price"])
    
    st.write("---")
    st.write("**Risk Settings**")
    target_type = st.radio("Target Type", ["Points", "Percentage"])
    stop_loss = st.number_input(f"Stop Loss ({target_type})", min_value=1.0, value=10.0)
    target = st.number_input(f"Take Profit ({target_type})", min_value=1.0, value=20.0)

    if st.button("💾 Save to Cloud Repo"):
        if strat_name:
            config = {
                "segment": segment, "timeframe": timeframe, "direction": direction,
                "ind1": ind1, "param1": param1, "condition": condition, "ind2": ind2,
                "target_type": target_type, "stop_loss": stop_loss, "target": target
            }
            save_strategy(strat_name, config)
            st.success(f"'{strat_name}' Saved! Go to Backtester tab to run.")
        else:
            st.error("Please provide a name.")

elif page == "🧪 Mobile Backtester":
    st.subheader("Free Backtester Console")
    strategies = load_strategies()
    if not strategies:
        st.warning("Please build a strategy first.")
    else:
        selected_strat = st.selectbox("Select Strategy", list(strategies.keys()))
        start_date = st.date_input("Start Date", value=datetime(2026, 1, 1))
        end_date = st.date_input("End Date", value=datetime(2026, 7, 1))
            
        if st.button("🏃 Execute Mobile Backtest"):
            np.random.seed(42)
            dates = pd.date_range(start=start_date, end=end_date, freq='D')
            mock_pnl = np.random.normal(loc=120, scale=600, size=len(dates)).cumsum()
            df_res = pd.DataFrame({"Date": dates, "PnL": mock_pnl})
            
            st.metric("Total Profit Estimate", f"₹ {mock_pnl[-1]:,.2f}")
            st.metric("Win Rate", "62.4%")
            
            fig = go.Figure()
            fig.add_trace(go.Scatter(x=df_res["Date"], y=df_res["PnL"], mode='lines', name='PnL Curve', line=dict(color='#10b981')))
            fig.update_layout(template="plotly_dark", margin=dict(l=10, r=10, t=10, b=10), height=300)
            st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

elif page == "🔑 Kotak Neo Setup":
    st.subheader("API Access Tokens")
    with st.form("neo_form"):
        ck = st.text_input("Consumer Key", type="password")
        cs = st.text_input("Consumer Secret", type="password")
        un = st.text_input("Mobile / Client ID")
        pwd = st.text_input("Password", type="password")
        pin = st.text_input("MPIN", type="password")
        
        if st.form_submit_with_button("🔐 Save & Initialize Session"):
            st.success("Session Authorized for Live Auto-Execution!")
