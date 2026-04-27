import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import os

os.makedirs('data', exist_ok=True)

# simulating 60 days of price history for a product
dates = [datetime.now() - timedelta(days=i) for i in range(60)]
dates.reverse()

base_price = 899
prices = []
for i in range(60):
    change = np.random.randint(-40, 40)
    base_price = max(600, min(1200, base_price + change))
    prices.append(base_price)

df = pd.DataFrame({
    'timestamp': dates,
    'name': 'Noise ColorFit Pro 4 Smartwatch',
    'price': prices,
    'url': 'https://www.amazon.in/dp/B08N5WRWNW'
})

df.to_csv('data/price_history.csv', index=False)
print("60 days of price data created successfully!")
print(df.tail(5))