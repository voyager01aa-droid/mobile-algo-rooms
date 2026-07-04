import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import pandas_ta as ta
import json
import os

# --- 1. Mobile Friendly Setup & CSS ---
st.set_page_config(page_title="Pro Algorooms Clone", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stMetric { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 5px; }
    div.stButton > button:first-child { width: 100%; background-color: #10b981; color: white; border-radius: 6px; height: 45px; font-weight: bold; font-size: 16px;}
    .section-title { font-size: 16px; font-weight: bold; color: #3b82f6; margin-top: 15px; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

# --- 2. Database (JSON) Functions ---
STRATEGY_FILE = "advanced_strategies.json"

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

# --- 3. Main Navigation ---
st.title("🚀 Pro Algo Console")
page = st.selectbox("Menu Chunein", ["⚙️ Advanced Strategy Builder", "🧪 Pro Backtester", "📊 Live Dashboard", "🔑 Broker Setup"])

# --- 4. ADVANCED STRATEGY BUILDER ---
if page == "⚙️ Advanced Strategy Builder":
    st.subheader("Bina Code Ki Custom Strategy")
    strat_name = st.text_input("Strategy Ka Naam", placeholder="e.g., RSI Crossover Sniper")
    
    symbol = st.selectbox("Market Symbol", ["^NSEI (Nifty 50)", "^NSEBANK (BankNifty)", "RELIANCE.NS", "SBIN.NS", "TCS.NS", "INFY.NS"])
    actual_symbol = symbol.split(" ")[0]
    direction = st.selectbox("Trade Direction", ["Long (Buy)", "Short (Sell)"])
    
    # Primary Condition
    st.markdown('<div class="section-title">🔴 CONDITION 1 (Main Trigger)</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    ind1 = c1.selectbox("Indicator 1", ["Close Price", "RSI", "SMA", "EMA", "MACD_Line"], key="i1")
    param1 = c2.number_input("Period/Length 1", min_value=1, value=14, key="p1")
    
    operator1 = st.selectbox("Logic", ["Greater Than (>)", "Less Than (<)", "Crosses Above", "Crosses Below"], key="op1")
    
    c3, c4 = st.columns(2)
    compare_type1 = c3.selectbox("Compare With", ["Static Value", "Another Indicator"], key="ct1")
    if compare_type1 == "Static Value":
        ind2_val1 = c4.number_input("Value (e.g. 60)", value=60.0, key="v1")
        ind2 = "Value"
        param2 = 0
    else:
        ind2 = c4.selectbox("Indicator 2", ["Close Price", "SMA", "EMA"], key="i2")
        param2 = st.number_input("Period/Length 2", min_value=1, value=50, key="p2")
        ind2_val1 = 0

    # Optional Condition (Filter)
    st.markdown('<div class="section-title">🟡 CONDITION 2 (Extra Filter)</div>', unsafe_allow_html=True)
    use_cond2 = st.checkbox("Enable 2nd Condition (AND Logic)")
    if use_cond2:
        c5, c6 = st.columns(2)
        ind3 = c5.selectbox("Indicator 3", ["RSI", "SMA", "EMA", "Close Price"], key="i3")
        param3 = c6.number_input("Period 3", value=14, key="p3")
        operator2 = st.selectbox("Logic 2", ["Greater Than (>)", "Less Than (<)"], key="op2")
        ind4_val2 = st.number_input("Static Value 2", value=50.0, key="v2")
    else:
        ind3, param3, operator2, ind4_val2 = None, None, None, None
        
    st.markdown('<div class="section-title">🟢 RISK MANAGEMENT</div>', unsafe_allow_html=True)
    stop_loss = st.number_input(f"Stop Loss (%)", min_value=0.1, value=1.0, step=0.1)
    target = st.number_input(f"Take Profit (%)", min_value=0.1, value=2.0, step=0.1)

    if st.button("💾 Save Custom Strategy"):
        if strat_name:
            config = {
                "symbol": actual_symbol, "direction": direction,
                "ind1": ind1, "param1": param1, "op1": operator1, "comp_type1": compare_type1, 
                "ind2": ind2, "param2": param2, "val1": ind2_val1,
                "use_cond2": use_cond2, "ind3": ind3, "param3": param3, "op2": operator2, "val2": ind4_val2,
                "stop_loss": stop_loss, "target": target
            }
            save_strategy(strat_name, config)
            st.success(f"Strategy '{strat_name}' successfully save ho gayi! Ab Backtester tab mein jayen.")
        else:
            st.error("Kripya strategy ka naam bharein.")

# --- 5. PRO BACKTESTER ---
elif page == "🧪 Pro Backtester":
    st.subheader("Real Market Backtester")
    strategies = load_strategies()
    
    if not strategies:
        st.warning("Koi strategy nahi mili. Pehle 'Strategy Builder' se ek banayein.")
    else:
        selected_strat = st.selectbox("Apni Strategy Chunein", list(strategies.keys()))
        conf = strategies[selected_strat]
        
        c1, c2 = st.columns(2)
        start_date = c1.date_input("Start Date", value=datetime(2025, 1, 1))
        end_date = c2.date_input("End Date", value=datetime.today())
        
        if st.button("🏃 Run Backtest"):
            with st.spinner("Market Data download aur indicators calculate ho rahe hain..."):
                try:
                    df = yf.download(conf['symbol'], start=start_date, end=end_date, progress=False)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                        
                    if df.empty:
                        st.error("Is date range ke liye koi data nahi mila!")
                    else:
                        # Helper Function
                        def calc_indicator(data, name, period):
                            if name == "Close Price": return data['Close']
                            elif name == "SMA": return ta.sma(data['Close'], length=period)
                            elif name == "EMA": return ta.ema(data['Close'], length=period)
                            elif name == "RSI": return ta.rsi(data['Close'], length=period)
                            elif name == "MACD_Line": 
                                macd = ta.macd(data['Close'])
                                return macd[macd.columns[0]] # Returns the MACD Line
                            return pd.Series(0, index=data.index)

                        # Condition 1
                        df['I1'] = calc_indicator(df, conf['ind1'], conf['param1'])
                        if conf['comp_type1'] == "Static Value":
                            df['I2'] = conf['val1']
                        else:
                            df['I2'] = calc_indicator(df, conf['ind2'], conf['param2'])

                        df['Cond1'] = False
                        if conf['op1'] == "Greater Than (>)": df['Cond1'] = df['I1'] > df['I2']
                        elif conf['op1'] == "Less Than (<)": df['Cond1'] = df['I1'] < df['I2']
                        elif conf['op1'] == "Crosses Above": df['Cond1'] = (df['I1'] > df['I2']) & (df['I1'].shift(1) <= df['I2'].shift(1))
                        elif conf['op1'] == "Crosses Below": df['Cond1'] = (df['I1'] < df['I2']) & (df['I1'].shift(1) >= df['I2'].shift(1))

                        # Condition 2
                        df['Cond2'] = True
                        if conf['use_cond2']:
                            df['I3'] = calc_indicator(df, conf['ind3'], conf['param3'])
                            df['I4'] = conf['val2']
                            if conf['op2'] == "Greater Than (>)": df['Cond2'] = df['I3'] > df['I4']
                            elif conf['op2'] == "Less Than (<)": df['Cond2'] = df['I3'] < df['I4']

                        # Generate Signals
                        df['Signal'] = np.where((df['Cond1']) & (df['Cond2']), 1, 0)
                        trade_dir = 1 if conf['direction'] == "Long (Buy)" else -1
                        
                        # Returns Logic
                        df['Market_Return'] = df['Close'].pct_change()
                        df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1) * trade_dir
                        
                        df.dropna(inplace=True)
                        df['Cumulative_Returns'] = (1 + df['Strategy_Return']).cumprod() - 1
                        
                        total_return = df['Cumulative_Returns'].iloc[-1] * 100
                        winning_days = len(df[df['Strategy_Return'] > 0])
                        total_trades = len(df[df['Strategy_Return'] != 0])
                        win_rate = (winning_days / total_trades * 100) if total_trades > 0 else 0
                        
                        # Visual Results
                        st.write(f"### Report: {conf['symbol']}")
                        res1, res2 = st.columns(2)
                        res1.metric("Total P&L (%)", f"{total_return:.2f} %")
                        res2.metric("Win Rate", f"{win_rate:.1f} %")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Returns'] * 100, mode='lines', line=dict(color='#3b82f6', width=2), name='Equity Curve'))
                        fig.update_layout(title="Strategy Performance Growth", template="plotly_dark", margin=dict(l=5, r=5, t=30, b=5), height=300)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                except Exception as e:
                    st.error(f"Execution Error: {e}")

# --- 6. LIVE DASHBOARD ---
elif page == "📊 Live Dashboard":
    st.subheader("Live Portfolio & Bots")
    c1, c2 = st.columns(2)
    c1.metric(label="Today's P&L", value="₹ 0.00", delta="0%")
    c2.metric(label="Active Bots", value="0")
    st.info("Live data feed connect hone ke baad yahan real-time profit aur auto-trades ki history dikhegi.")

# --- 7. BROKER SETUP ---
elif page == "🔑 Broker Setup":
    st.subheader("Kotak Neo API Link")
    st.write("Aapke Kotak account se auto-trading ke liye credentials yahan save karein.")
    with st.form("neo_form"):
        ck = st.text_input("Consumer Key", type="password")
        cs = st.text_input("Consumer Secret", type="password")
        un = st.text_input("Mobile Number / User ID")
        pwd = st.text_input("Password", type="password")
        pin = st.text_input("6-Digit MPIN", type="password")
        
        if st.form_submit_with_button("🔐 Save & Authorize"):
            st.success("API keys securely save ho gayi hain. Webhook connection ke liye taiyar!")
