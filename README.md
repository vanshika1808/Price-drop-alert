#  Price Drop Alert System

An end-to-end AI/ML project that tracks e-commerce product prices, predicts future price trends using machine learning, and sends automated email alerts when prices drop below your target.

**Live Demo:** [vanshika-price-alert.streamlit.app](https://vanshika-price-alert.streamlit.app)

---

##  Features

- **Price Scraping** — Collects product price data using BeautifulSoup and Requests
- **ML Price Prediction** — Trains and compares 3 models (Linear Regression, Random Forest, XGBoost) to forecast 7-day price trends
- **Automated Email Alerts** — Sends formatted HTML emails via Gmail SMTP when price drops below user-defined target
- **Smart Scheduler** — Runs price checks automatically every 6 hours using APScheduler
- **Interactive Dashboard** — Live Streamlit app with Plotly charts showing price history, predictions, and Buy/Wait recommendations

---

##  Tech Stack

| Category | Tools |
|---|---|
| Language | Python 3.11 |
| Data Collection | BeautifulSoup4, Requests |
| Data Processing | Pandas, NumPy |
| Machine Learning | Scikit-learn, XGBoost |
| Visualization | Matplotlib, Plotly |
| Web App | Streamlit |
| Email Automation | SMTP, smtplib |
| Scheduling | APScheduler |
| Model Persistence | Joblib |
| Environment | Python-dotenv |

---

##  Project Structure

```
price-drop-alert/
├── scraper.py          # Web scraping engine
├── ml_model.py         # ML model training & prediction
├── alert.py            # Email alert system + scheduler
├── app.py              # Streamlit dashboard
├── generate_data.py    # Sample data generator
├── requirements.txt    # Dependencies
├── data/
│   ├── price_history.csv       # Historical price data
│   └── price_prediction.png    # Prediction chart
└── models/
    └── best_model.pkl          # Saved best ML model
```

---

##  How It Works

```
1. scraper.py     →  Scrapes product price from e-commerce site
2. CSV storage    →  Saves timestamped price history
3. ml_model.py    →  Feature engineering + trains 3 ML models
4. Model selection →  Picks best model by lowest RMSE
5. Prediction     →  Forecasts next 7 days of prices
6. alert.py       →  Compares current price vs target price
7. Email sent     →  HTML alert with prediction table + Buy/Wait recommendation
8. Streamlit app  →  Live dashboard showing everything visually
```

---

##  ML Model Results

| Model | MAE | RMSE |
|---|---|---|
| Linear Regression | ₹58.13 | ₹63.43 |
| Random Forest | ₹120.39 | ₹133.94 |
| XGBoost | ₹131.95 | ₹146.39 |

**Best Model:** Linear Regression (lowest RMSE)

---

##  Setup & Installation

### 1. Clone the repository
```bash
git clone https://github.com/vanshika1808/Price-drop-alert.git
cd Price-drop-alert
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment variables
Create a `.env` file:
```
EMAIL_SENDER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
EMAIL_RECEIVER=your_email@gmail.com
TARGET_PRICE=1000
```

### 4. Generate sample data
```bash
python generate_data.py
```

### 5. Train the ML model
```bash
python ml_model.py
```

### 6. Start the dashboard
```bash
streamlit run app.py
```

---

##  Email Alert System

The system sends three types of alerts:

-  **BUY NOW** — Current price is below your target
-  **WAIT — Price dropping soon** — ML predicts price will drop within 7 days
-  **WAIT — Price still high** — Price is above target with no drop predicted

---

##  Deployment

Deployed on **Streamlit Community Cloud** — free hosting for Streamlit apps.

Live URL: [vanshika-price-alert.streamlit.app](https://vanshika-price-alert.streamlit.app)

---

##  Author

**Vanshika Mukati**
- GitHub: [@vanshika1808](https://github.com/vanshika1808)
- Email: vanshikam8141@gmail.com

---

##  License

This project is open source and available under the [MIT License](LICENSE).
