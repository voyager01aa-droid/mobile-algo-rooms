import streamlit as st
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from datetime import datetime
import yfinance as yf
import ta
import json
import os

# --- Mobile Friendly Setup ---
st.set_page_config(page_title="Ultra Pro Algorooms", layout="centered", initial_sidebar_state="collapsed")

st.markdown("""
    <style>
    .stMetric { background-color: #1e293b; padding: 10px; border-radius: 8px; border: 1px solid #334155; margin-bottom: 5px; }
    div.stButton > button:first-child { width: 100%; background-color: #3b82f6; color: white; border-radius: 6px; height: 45px; font-weight: bold; font-size: 16px;}
    .section-title { font-size: 16px; font-weight: bold; color: #10b981; margin-top: 15px; margin-bottom: 5px;}
    </style>
""", unsafe_allow_html=True)

STRATEGY_FILE = "ultra_strategies.json"

def load_strategies():
    if os.path.exists(STRATEGY_FILE):
        try:
            with open(STRATEGY_FILE, 'r') as f: return json.load(f)
        except: return {}
    return {}

def save_strategy(name, config):
    strategies = load_strategies()
    strategies[name] = config
    with open(STRATEGY_FILE, 'w') as f: json.dump(strategies, f, indent=4)

st.title("🚀 Advanced Algo Builder")
page = st.selectbox("Menu Chunein", ["⚙️ Strategy Builder", "🧪 Pro Backtester", "📊 Live Dashboard", "🔑 Broker Setup"])

# Stable Indicators List
INDICATOR_LIST = [
    "Close Price", "RSI", "SMA", "EMA", "MACD_Line", 
    "Bollinger_Upper", "Bollinger_Lower", "ATR", 
    "ADX", "Stochastic_K", "CCI"
]

if page == "⚙️ Strategy Builder":
    st.subheader("Bina Code Ki Custom Strategy")
    strat_name = st.text_input("Strategy Ka Naam", placeholder="e.g., RSI + Bollinger Sniper")
    
    symbol = st.selectbox("Market Symbol", ["^NSEI (Nifty 50)", "^NSEBANK (BankNifty)", "RELIANCE.NS", "SBIN.NS"])
    actual_symbol = symbol.split(" ")[0]
    direction = st.selectbox("Trade Direction", ["Long (Buy)", "Short (Sell)"])
    
    st.markdown('<div class="section-title">🔴 MAIN TRIGGER</div>', unsafe_allow_html=True)
    c1, c2 = st.columns(2)
    ind1 = c1.selectbox("Indicator 1", INDICATOR_LIST, key="i1")
    param1 = c2.number_input("Period (Length)", min_value=1, value=14, key="p1")
    
    operator1 = st.selectbox("Logic", ["Greater Than (>)", "Less Than (<)", "Crosses Above", "Crosses Below"], key="op1")
    
    c3, c4 = st.columns(2)
    compare_type1 = c3.selectbox("Compare With", ["Static Value", "Another Indicator"], key="ct1")
    if compare_type1 == "Static Value":
        ind2_val1 = c4.number_input("Value", value=60.0, key="v1")
        ind2 = "Value"
        param2 = 0
    else:
        ind2 = c4.selectbox("Indicator 2", INDICATOR_LIST, key="i2")
        param2 = st.number_input("Period 2", min_value=1, value=50, key="p2")
        ind2_val1 = 0

    st.markdown('<div class="section-title">🟡 EXTRA FILTER (AND LOGIC)</div>', unsafe_allow_html=True)
    use_cond2 = st.checkbox("Enable 2nd Condition")
    if use_cond2:
        c5, c6 = st.columns(2)
        ind3 = c5.selectbox("Indicator 3", INDICATOR_LIST, key="i3")
        param3 = c6.number_input("Period 3", value=14, key="p3")
        operator2 = st.selectbox("Logic 2", ["Greater Than (>)", "Less Than (<)"], key="op2")
        ind4_val2 = st.number_input("Static Value 2", value=50.0, key="v2")
    else:
        ind3, param3, operator2, ind4_val2 = None, None, None, None
        
    st.markdown('<div class="section-title">🟢 RISK MANAGEMENT</div>', unsafe_allow_html=True)
    stop_loss = st.number_input(f"Stop Loss (%)", min_value=0.1, value=1.0, step=0.1)
    target = st.number_input(f"Take Profit (%)", min_value=0.1, value=2.0, step=0.1)

    if st.button("💾 Save Strategy"):
        if strat_name:
            config = {
                "symbol": actual_symbol, "direction": direction,
                "ind1": ind1, "param1": param1, "op1": operator1, "comp_type1": compare_type1, 
                "ind2": ind2, "param2": param2, "val1": ind2_val1,
                "use_cond2": use_cond2, "ind3": ind3, "param3": param3, "op2": operator2, "val2": ind4_val2,
                "stop_loss": stop_loss, "target": target
            }
            save_strategy(strat_name, config)
            st.success("Save ho gayi! Ab Backtester tab mein jayen.")
        else:
            st.error("Kripya naam bharein.")

elif page == "🧪 Pro Backtester":
    st.subheader("Error-Free Backtest Engine")
    strategies = load_strategies()
    
    if not strategies:
        st.warning("Pehle Strategy Builder se ek banayein.")
    else:
        selected_strat = st.selectbox("Select Strategy", list(strategies.keys()))
        conf = strategies[selected_strat]
        
        c1, c2 = st.columns(2)
        start_date = c1.date_input("Start Date", value=datetime(2025, 1, 1))
        end_date = c2.date_input("End Date", value=datetime.today())
        
        if st.button("🏃 Run Backtest"):
            with st.spinner("Market Data aur Indicators calculate ho rahe hain..."):
                try:
                    df = yf.download(conf['symbol'], start=start_date, end=end_date, progress=False)
                    if isinstance(df.columns, pd.MultiIndex):
                        df.columns = df.columns.get_level_values(0)
                        
                    if df.empty:
                        st.error("Data nahi mila!")
                    else:
                        # --- CRASH-FREE ENGINE ---
                        def calc_indicator(data, name, period):
                            period = int(period)
                            close = data['Close']
                            
                            if name == "Close Price": return close
                            elif name == "SMA": return ta.trend.sma_indicator(close, window=period)
                            elif name == "EMA": return ta.trend.ema_indicator(close, window=period)
                            elif name == "RSI": return ta.momentum.rsi(close, window=period)
                            elif name == "MACD_Line": return ta.trend.macd(close)
                            elif name == "Bollinger_Upper": return ta.volatility.bollinger_hband(close, window=period)
                            elif name == "Bollinger_Lower": return ta.volatility.bollinger_lband(close, window=period)
                            elif name == "ATR": return ta.volatility.average_true_range(data['High'], data['Low'], close, window=period)
                            elif name == "ADX": return ta.trend.adx(data['High'], data['Low'], close, window=period)
                            elif name == "Stochastic_K": return ta.momentum.stoch(data['High'], data['Low'], close, window=period)
                            elif name == "CCI": return ta.trend.cci(data['High'], data['Low'], close, window=period)
                            
                            return pd.Series(0, index=data.index)

                        df['I1'] = calc_indicator(df, conf['ind1'], conf['param1'])
                        if conf['comp_type1'] == "Static Value": df['I2'] = conf['val1']
                        else: df['I2'] = calc_indicator(df, conf['ind2'], conf['param2'])

                        df['Cond1'] = False
                        if conf['op1'] == "Greater Than (>)": df['Cond1'] = df['I1'] > df['I2']
                        elif conf['op1'] == "Less Than (<)": df['Cond1'] = df['I1'] < df['I2']
                        elif conf['op1'] == "Crosses Above": df['Cond1'] = (df['I1'] > df['I2']) & (df['I1'].shift(1) <= df['I2'].shift(1))
                        elif conf['op1'] == "Crosses Below": df['Cond1'] = (df['I1'] < df['I2']) & (df['I1'].shift(1) >= df['I2'].shift(1))

                        df['Cond2'] = True
                        if conf['use_cond2']:
                            df['I3'] = calc_indicator(df, conf['ind3'], conf['param3'])
                            df['I4'] = conf['val2']
                            if conf['op2'] == "Greater Than (>)": df['Cond2'] = df['I3'] > df['I4']
                            elif conf['op2'] == "Less Than (<)": df['Cond2'] = df['I3'] < df['I4']

                        df['Signal'] = np.where((df['Cond1']) & (df['Cond2']), 1, 0)
                        trade_dir = 1 if conf['direction'] == "Long (Buy)" else -1
                        
                        df['Market_Return'] = df['Close'].pct_change()
                        df['Strategy_Return'] = df['Market_Return'] * df['Signal'].shift(1) * trade_dir
                        
                        df.dropna(inplace=True)
                        df['Cumulative_Returns'] = (1 + df['Strategy_Return']).cumprod() - 1
                        
                        total_return = df['Cumulative_Returns'].iloc[-1] * 100
                        winning_days = len(df[df['Strategy_Return'] > 0])
                        total_trades = len(df[df['Strategy_Return'] != 0])
                        win_rate = (winning_days / total_trades * 100) if total_trades > 0 else 0
                        
                        st.write(f"### Report: {conf['symbol']}")
                        res1, res2 = st.columns(2)
                        res1.metric("Total P&L (%)", f"{total_return:.2f} %")
                        res2.metric("Win Rate", f"{win_rate:.1f} %")
                        
                        fig = go.Figure()
                        fig.add_trace(go.Scatter(x=df.index, y=df['Cumulative_Returns'] * 100, mode='lines', line=dict(color='#3b82f6', width=2)))
                        fig.update_layout(title="Equity Curve", template="plotly_dark", margin=dict(l=5, r=5, t=30, b=5), height=300)
                        st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})
                        
                except Exception as e:
                    st.error(f"Execution Error: {e}")

elif page == "📊 Live Dashboard":
    st.info("Live Dashboard under construction.")
elif page == "🔑 Broker Setup":
    st.info("Kotak Neo Credentials form...")
