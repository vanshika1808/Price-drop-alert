import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import joblib
import os
from datetime import datetime
import numpy as np

st.set_page_config(
    page_title="Price Drop Alert System",
    page_icon="💰",
    layout="wide"
)

st.title("💰 Price Drop Alert System")
st.markdown("Track product prices, predict trends & get buy/wait recommendations")

def load_data():
    if os.path.exists('data/price_history.csv'):
        df = pd.read_csv('data/price_history.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)
        return df
    return None

def get_predictions(df):
    try:
        saved = joblib.load('models/best_model.pkl')
        model = saved['model']

        df['day_index'] = range(len(df))
        df['day_of_week'] = df['timestamp'].dt.dayofweek
        df['rolling_avg_7'] = df['price'].rolling(7, min_periods=1).mean()
        df['rolling_avg_14'] = df['price'].rolling(14, min_periods=1).mean()
        df['price_lag1'] = df['price'].shift(1).fillna(df['price'].mean())
        df['price_lag3'] = df['price'].shift(3).fillna(df['price'].mean())

        future_prices = []
        temp_df = df.copy()

        for i in range(7):
            next_idx = len(temp_df)
            next_row = {
                'day_index': next_idx,
                'day_of_week': next_idx % 7,
                'rolling_avg_7': temp_df['price'].tail(7).mean(),
                'rolling_avg_14': temp_df['price'].tail(14).mean(),
                'price_lag1': temp_df['price'].iloc[-1],
                'price_lag3': temp_df['price'].iloc[-3]
            }
            pred = model.predict(pd.DataFrame([next_row]))[0]
            future_prices.append(round(float(pred), 2))
            new_row = pd.DataFrame([{**next_row, 'price': pred,
                                      'timestamp': pd.Timestamp.now(),
                                      'name': '', 'url': ''}])
            temp_df = pd.concat([temp_df, new_row], ignore_index=True)

        return future_prices
    except Exception as e:
        st.error(f"Prediction error: {e}")
        return []

df = load_data()

if df is not None:
    current_price = df['price'].iloc[-1]
    product_name = df['name'].iloc[-1]
    min_price = df['price'].min()
    max_price = df['price'].max()
    avg_price = df['price'].mean()

    st.sidebar.header("Set Your Target Price")
    target_price = st.sidebar.number_input(
        "Target Price (₹)",
        min_value=int(min_price * 0.5),
        max_value=int(max_price * 1.5),
        value=int(avg_price * 0.9),
        step=10
    )
    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**Product:** {product_name}")
    st.sidebar.markdown(f"**Data Points:** {len(df)} days")
    st.sidebar.markdown(f"**Last Updated:** {df['timestamp'].iloc[-1].strftime('%Y-%m-%d')}")

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current Price", f"₹{current_price:.0f}")
    with col2:
        st.metric("Your Target", f"₹{target_price:.0f}",
                  delta=f"₹{current_price - target_price:.0f} away")
    with col3:
        st.metric("Lowest Ever", f"₹{min_price:.0f}")
    with col4:
        st.metric("Highest Ever", f"₹{max_price:.0f}")

    st.markdown("---")

    future_prices = get_predictions(df)
    future_dates = pd.date_range(
        start=df['timestamp'].iloc[-1], periods=8, freq='D')[1:]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=df['timestamp'], y=df['price'],
        mode='lines', name='Historical Price',
        line=dict(color='#2196F3', width=2)
    ))
    fig.add_trace(go.Scatter(
        x=future_dates, y=future_prices,
        mode='lines+markers', name='Predicted Price',
        line=dict(color='#FF9800', width=2, dash='dash'),
        marker=dict(size=8)
    ))
    fig.add_hline(
        y=target_price, line_dash="dot",
        line_color="green",
        annotation_text=f"Your Target ₹{target_price}"
    )
    fig.update_layout(
        title='Price History + 7-Day ML Prediction',
        xaxis_title='Date',
        yaxis_title='Price (₹)',
        hovermode='x unified',
        height=450
    )
    st.plotly_chart(fig, use_container_width=True)

    st.markdown("---")
    st.subheader("AI Recommendation")

    min_predicted = min(future_prices) if future_prices else current_price

    if current_price <= target_price:
        st.success("## ✅ BUY NOW!")
        st.success(f"Current price ₹{current_price:.0f} is below your target ₹{target_price}!")
    elif min_predicted <= target_price:
        st.warning("## ⏳ WAIT — Price dropping soon!")
        st.warning(f"Price predicted to drop to ₹{min_predicted:.0f} within 7 days!")
    else:
        st.error("## ❌ WAIT — Price still high")
        st.error(f"Current ₹{current_price:.0f} is ₹{current_price - target_price:.0f} above your target.")

    st.markdown("---")
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("7-Day Price Prediction")
        pred_df = pd.DataFrame({
            'Day': [f"Day {i+1}" for i in range(7)],
            'Date': [d.strftime('%b %d') for d in future_dates],
            'Predicted Price': [f"₹{p:.0f}" for p in future_prices],
            'vs Current': [f"{'▼' if p < current_price else '▲'} ₹{abs(p - current_price):.0f}"
                          for p in future_prices]
        })
        st.dataframe(pred_df, hide_index=True, use_container_width=True)

    with col2:
        st.subheader("Price Statistics")
        stats_df = pd.DataFrame({
            'Metric': ['Current Price', 'Target Price', 'Lowest Price',
                      'Highest Price', 'Average Price', 'Price Range'],
            'Value': [f"₹{current_price:.0f}", f"₹{target_price:.0f}",
                     f"₹{min_price:.0f}", f"₹{max_price:.0f}",
                     f"₹{avg_price:.0f}", f"₹{max_price - min_price:.0f}"]
        })
        st.dataframe(stats_df, hide_index=True, use_container_width=True)

else:
    st.error("No price data found! Please run generate_data.py first.")