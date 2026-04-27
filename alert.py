import traceback
import sys
print("Script started...")
sys.stdout.flush()



import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
import pandas as pd
import joblib
import os
from dotenv import load_dotenv
from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime

load_dotenv()

SENDER = os.getenv('EMAIL_SENDER')
PASSWORD = os.getenv('EMAIL_PASSWORD')
RECEIVER = os.getenv('EMAIL_RECEIVER')
TARGET_PRICE = float(os.getenv('TARGET_PRICE', 1050))


def get_latest_price():
    df = pd.read_csv('data/price_history.csv')
    latest = df.iloc[-1]
    return latest['price'], latest['name']


def get_predicted_prices():
    try:
        saved = joblib.load('models/best_model.pkl')
        model = saved['model']
        df = pd.read_csv('data/price_history.csv')
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df = df.sort_values('timestamp').reset_index(drop=True)

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
        print(f"Prediction error: {e}")
        return []


def send_email(subject, html_body):
    try:
        msg = MIMEMultipart('alternative')
        msg['Subject'] = subject
        msg['From'] = SENDER
        msg['To'] = RECEIVER
        msg.attach(MIMEText(html_body, 'html'))

        with smtplib.SMTP_SSL('smtp.gmail.com', 465) as server:
            server.login(SENDER, PASSWORD)
            server.sendmail(SENDER, RECEIVER, msg.as_string())

        print(f"Email sent successfully to {RECEIVER}")
        return True
    except Exception as e:
        print(f"Email error: {e}")
        return False


def check_and_alert():
    print(f"\n[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] Checking price...")

    current_price, product_name = get_latest_price()
    predicted_prices = get_predicted_prices()

    print(f"Product: {product_name}")
    print(f"Current Price: ₹{current_price}")
    print(f"Target Price: ₹{TARGET_PRICE}")

    min_predicted = min(predicted_prices) if predicted_prices else current_price
    prediction_rows = ''.join([
        f"<tr><td style='padding:6px;'>Day {i+1}</td>"
        f"<td style='padding:6px;color:{'green' if p < current_price else 'red'}'>₹{p}</td></tr>"
        for i, p in enumerate(predicted_prices)
    ])

    if current_price <= TARGET_PRICE:
        subject = f"Price Drop Alert! {product_name} is now ₹{current_price}"
        recommendation = "BUY NOW"
        rec_color = "#27ae60"
        message = f"Great news! The price has dropped to ₹{current_price}, below your target of ₹{TARGET_PRICE}!"
    elif min_predicted <= TARGET_PRICE:
        subject = f"Price Expected to Drop Soon! {product_name}"
        recommendation = "WAIT & WATCH"
        rec_color = "#f39c12"
        message = f"Current price ₹{current_price} is above target, but predicted to drop to ₹{min_predicted:.0f} soon!"
    else:
        subject = f"Price Update: {product_name} = ₹{current_price}"
        recommendation = "WAIT"
        rec_color = "#e74c3c"
        message = f"Current price ₹{current_price} is above your target of ₹{TARGET_PRICE}. Waiting for a better deal."

    html_body = f"""
    <html><body style="font-family:Arial,sans-serif;max-width:600px;margin:auto;">
      <h2 style="color:#2c3e50;">Price Drop Alert System</h2>
      <div style="background:#f8f9fa;padding:15px;border-radius:8px;margin:10px 0;">
        <h3>{product_name}</h3>
        <p>{message}</p>
        <table>
          <tr><td><b>Current Price:</b></td><td>₹{current_price}</td></tr>
          <tr><td><b>Your Target:</b></td><td>₹{TARGET_PRICE}</td></tr>
        </table>
      </div>
      <div style="text-align:center;padding:15px;">
        <span style="background:{rec_color};color:white;padding:10px 25px;
                     border-radius:5px;font-size:18px;font-weight:bold;">
          {recommendation}
        </span>
      </div>
      <h4>7-Day Price Prediction:</h4>
      <table border="1" cellpadding="5" style="border-collapse:collapse;">
        <tr style="background:#2c3e50;color:white;">
          <th style="padding:6px;">Day</th>
          <th style="padding:6px;">Predicted Price</th>
        </tr>
        {prediction_rows}
      </table>
      <p style="color:#888;font-size:12px;margin-top:20px;">
        Sent by Price Drop Alert System — {datetime.now().strftime('%Y-%m-%d %H:%M')}
      </p>
    </body></html>
    """

    send_email(subject, html_body)


def run_scheduler():
    print("Scheduler started — checking price every 6 hours...")
    print("Press Ctrl+C to stop\n")
    scheduler = BlockingScheduler()
    scheduler.add_job(check_and_alert, 'interval', hours=6)
    check_and_alert()
    scheduler.start()


if __name__ == "__main__":
    try:
     run_scheduler()
    except Exception as e:
        traceback.print_exc()
        input("Press Enter to exit...")