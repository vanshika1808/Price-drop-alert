import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error
from xgboost import XGBRegressor
import joblib
import matplotlib.pyplot as plt
import os

os.makedirs('models', exist_ok=True)

def load_and_prepare_data():
    df = pd.read_csv('data/price_history.csv')
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    df = df.sort_values('timestamp').reset_index(drop=True)

    # feature engineering
    df['day_index'] = range(len(df))
    df['day_of_week'] = df['timestamp'].dt.dayofweek
    df['rolling_avg_7'] = df['price'].rolling(window=7, min_periods=1).mean()
    df['rolling_avg_14'] = df['price'].rolling(window=14, min_periods=1).mean()
    df['price_lag1'] = df['price'].shift(1).fillna(df['price'].mean())
    df['price_lag3'] = df['price'].shift(3).fillna(df['price'].mean())

    return df

def train_models(df):
    features = ['day_index', 'day_of_week', 'rolling_avg_7', 
                'rolling_avg_14', 'price_lag1', 'price_lag3']
    
    X = df[features]
    y = df['price']

    # 80/20 train test split
    split = int(len(df) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    models = {
        'Linear Regression': LinearRegression(),
        'Random Forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'XGBoost': XGBRegressor(n_estimators=100, random_state=42, verbosity=0)
    }

    results = {}
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        mae = mean_absolute_error(y_test, preds)
        rmse = np.sqrt(mean_squared_error(y_test, preds))
        results[name] = {'model': model, 'mae': mae, 'rmse': rmse, 'preds': preds}
        print(f"{name} → MAE: ₹{mae:.2f}  RMSE: ₹{rmse:.2f}")

    return results, X_test, y_test, features

def save_best_model(results, features):
    best_name = min(results, key=lambda x: results[x]['rmse'])
    best_model = results[best_name]['model']
    joblib.dump({'model': best_model, 'features': features}, 'models/best_model.pkl')
    print(f"\nBest model: {best_name} — saved to models/best_model.pkl")
    return best_name

def predict_next_7_days(df, features):
    saved = joblib.load('models/best_model.pkl')
    model = saved['model']

    last_row = df.iloc[-1]
    future_prices = []
    temp_df = df.copy()

    for i in range(7):
        next_idx = len(temp_df)
        next_row = {
            'day_index': next_idx,
            'day_of_week': (next_idx) % 7,
            'rolling_avg_7': temp_df['price'].tail(7).mean(),
            'rolling_avg_14': temp_df['price'].tail(14).mean(),
            'price_lag1': temp_df['price'].iloc[-1],
            'price_lag3': temp_df['price'].iloc[-3]
        }
        pred = model.predict(pd.DataFrame([next_row]))[0]
        future_prices.append(round(pred, 2))
        new_row = pd.DataFrame([{**next_row, 'price': pred, 
                                  'timestamp': pd.Timestamp.now(), 
                                  'name': '', 'url': ''}])
        temp_df = pd.concat([temp_df, new_row], ignore_index=True)

    print("\nPredicted prices for next 7 days:")
    for i, p in enumerate(future_prices, 1):
        print(f"  Day {i}: ₹{p}")
    
    return future_prices

def plot_prices(df, future_prices):
    plt.figure(figsize=(12, 5))
    plt.plot(df['timestamp'], df['price'], label='Historical Price', color='blue')
    
    future_dates = pd.date_range(
        start=df['timestamp'].iloc[-1], periods=8, freq='D')[1:]
    plt.plot(future_dates, future_prices, 
             label='Predicted Price', color='orange', linestyle='--', marker='o')
    
    plt.title('Price History + 7-Day Prediction')
    plt.xlabel('Date')
    plt.ylabel('Price (₹)')
    plt.legend()
    plt.tight_layout()
    plt.savefig('data/price_prediction.png')
    plt.show()
    print("\nChart saved to data/price_prediction.png")

if __name__ == "__main__":
    print("Loading data...")
    df = load_and_prepare_data()
    
    print("\nTraining models...")
    results, X_test, y_test, features = train_models(df)
    
    best = save_best_model(results, features)
    
    print("\nPredicting next 7 days...")
    future_prices = predict_next_7_days(df, features)
    
    print("\nGenerating chart...")
    plot_prices(df, future_prices)