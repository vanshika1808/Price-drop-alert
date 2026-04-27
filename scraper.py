import requests
from bs4 import BeautifulSoup
import pandas as pd
from datetime import datetime
import os

def scrape_price(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                      'AppleWebKit/537.36 (KHTML, like Gecko) '
                      'Chrome/120.0.0.0 Safari/537.36'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')

        # scrape product name
        name = soup.find('span', {'id': 'productTitle'})
        name = name.get_text(strip=True) if name else "Unknown Product"

        # scrape price
        price = soup.find('span', {'class': 'a-price-whole'})
        price = price.get_text(strip=True).replace(',', '') if price else None

        if price:
            price = float(price)
        else:
            print("Price not found — Amazon may have blocked the request")
            return None

        print(f"Product: {name}")
        print(f"Price: ₹{price}")
        return {'name': name, 'price': price}

    except Exception as e:
        print(f"Error scraping: {e}")
        return None


def save_price(url, data):
    filepath = 'data/price_history.csv'
    
    row = {
        'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'url': url,
        'name': data['name'],
        'price': data['price']
    }

    df_new = pd.DataFrame([row])

    if os.path.exists(filepath):
        df_existing = pd.read_csv(filepath)
        df = pd.concat([df_existing, df_new], ignore_index=True)
    else:
        df = df_new

    df.to_csv(filepath, index=False)
    print(f"Price saved to {filepath}")


def run_scraper(url):
    print(f"\nScraping: {url}")
    data = scrape_price(url)
    if data:
        save_price(url, data)
        return data
    return None


if __name__ == "__main__":
    # paste any amazon product URL here to test
    url = "https://www.amazon.in/dp/B08N5WRWNW"
    run_scraper(url)