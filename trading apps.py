import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import time
from datetime import datetime

# Initialize session state
if 'portfolio' not in st.session_state:
    st.session_state.portfolio = {}
if 'transactions' not in st.session_state:
    st.session_state.transactions = []
if 'signals' not in st.session_state:
    st.session_state.signals = []

# Sample market data
def get_market_data():
    symbols = ['NTC', 'NBL', 'SCB', 'HIDCL', 'CIT', 'NICA', 'GBIME', 'NIFRA', 'SHL', 'NMB']
    data = {
        'Symbol': symbols,
        'Price': np.random.uniform(100, 2000, len(symbols)).round(2),
        'Change %': np.random.uniform(-5, 5, len(symbols)).round(2),
        'Volume': np.random.randint(10000, 100000, len(symbols))
    }
    return pd.DataFrame(data)

# Sample AI signals
def get_ai_signals():
    return [
        {'Symbol': 'NTC', 'Signal': 'BUY', 'Target': 1800, 'Stop Loss': 1600},
        {'Symbol': 'SCB', 'Signal': 'SELL', 'Target': 900, 'Stop Loss': 950},
        {'Symbol': 'HIDCL', 'Signal': 'HOLD', 'Target': 300, 'Stop Loss': 280}
    ]

# Execute trade function
def execute_trade(symbol, action, price, quantity):
    # Record transaction
    transaction = {
        'id': len(st.session_state.transactions) + 1,
        'symbol': symbol,
        'action': action,
        'quantity': quantity,
        'price': price,
        'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.transactions.append(transaction)
    
    # Update portfolio
    if symbol not in st.session_state.portfolio:
        st.session_state.portfolio[symbol] = {
            'shares': 0,
            'avg_price': 0,
            'target': 0,
            'stop_loss': 0
        }
    
    holding = st.session_state.portfolio[symbol]
    if action == "BUY":
        total_cost = holding['shares'] * holding['avg_price']
        total_cost += quantity * price
        holding['shares'] += quantity
        holding['avg_price'] = total_cost / holding['shares'] if holding['shares'] > 0 else 0
    elif action == "SELL":
        if holding['shares'] >= quantity:
            holding['shares'] -= quantity
            if holding['shares'] == 0:
                del st.session_state.portfolio[symbol]

# App UI
st.set_page_config(
    page_title="AI Trading System",
    page_icon="📈",
    layout="wide"
)

st.title("📈 AI-Powered Trading System")

# Dashboard Section
st.header("Dashboard")
market_data = get_market_data()
st.session_state.signals = get_ai_signals()

# Portfolio Summary
col1, col2, col3 = st.columns(3)
total_investment = sum(
    h['shares'] * h['avg_price'] 
    for h in st.session_state.portfolio.values()
)

# Fixed current_value calculation
current_value = 0
for symbol, data in st.session_state.portfolio.items():
    symbol_data = market_data[market_data['Symbol'] == symbol]
    if not symbol_data.empty:
        current_price = symbol_data['Price'].values[0]
        current_value += data['shares'] * current_price

total_pnl = current_value - total_investment

col1.metric("Total Investment", f"Rs {total_investment:,.2f}")
col2.metric("Current Value", f"Rs {current_value:,.2f}", 
            f"{'Rs +' if total_pnl >= 0 else 'Rs '}{total_pnl:,.2f}")
col3.metric("Active Holdings", f"{len(st.session_state.portfolio)}")

# Portfolio Holdings
st.subheader("Your Holdings")
if st.session_state.portfolio:
    holdings_data = []
    for symbol, data in st.session_state.portfolio.items():
        symbol_data = market_data[market_data['Symbol'] == symbol]
        current_price = symbol_data['Price'].values[0] if not symbol_data.empty else data['avg_price']
        holdings_data.append({
            'Symbol': symbol,
            'Shares': data['shares'],
            'Avg Price': data['avg_price'],
            'Current Price': current_price,
            'Value': data['shares'] * current_price,
            'P&L': (current_price - data['avg_price']) * data['shares']
        })
    
    holdings_df = pd.DataFrame(holdings_data)
    st.dataframe(holdings_df)
    
    # Portfolio chart
    fig = px.pie(holdings_df, names='Symbol', values='Value', 
                 title='Portfolio Allocation')
    st.plotly_chart(fig, use_container_width=True)
else:
    st.info("No holdings in your portfolio. Execute trades to get started.")

# Live Market Data
st.header("Live Market Data")
st.dataframe(market_data.sort_values('Change %', ascending=False))

# AI Signals
st.header("🤖 AI Trading Signals")
for signal in st.session_state.signals:
    color = "green" if signal['Signal'] == 'BUY' else "red" if signal['Signal'] == 'SELL' else "orange"
    with st.expander(f"{signal['Symbol']} - {signal['Signal']}", expanded=True):
        st.markdown(f"""
        <div style="border-left: 4px solid {color}; padding-left: 1rem;">
            <p><b>Action:</b> <span style="color:{color}">{signal['Signal']}</span></p>
            <p><b>Target:</b> Rs {signal['Target']:,.2f}</p>
            <p><b>Stop Loss:</b> Rs {signal['Stop Loss']:,.2f}</p>
        </div>
        """, unsafe_allow_html=True)

# Trade Execution
st.header("💱 Execute Trade")
symbol = st.selectbox("Select Symbol", market_data['Symbol'].tolist())
action = st.radio("Action", ["BUY", "SELL"], horizontal=True)
quantity = st.number_input("Quantity", min_value=1, value=100)
price = st.number_input("Price (Rs)", min_value=0.01, 
                        value=float(market_data[market_data['Symbol'] == symbol]['Price'].values[0]),
                        step=0.5, format="%.2f")

if st.button("Execute Trade"):
    execute_trade(symbol, action, price, quantity)
    st.success(f"Trade executed: {action} {quantity} shares of {symbol} at Rs {price:,.2f}")

# Transaction History
st.header("📝 Transaction History")
if st.session_state.transactions:
    trans_df = pd.DataFrame(st.session_state.transactions)
    st.dataframe(trans_df.sort_values('timestamp', ascending=False))
else:
    st.info("No transactions recorded yet")

# Auto-refresh
st.caption("Data refreshes every 30 seconds")
time.sleep(30)
st.rerun()  # FIXED: replaced experimental_rerun with rerun
