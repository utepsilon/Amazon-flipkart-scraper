import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

# Telegram bot token and user ID
bot_token = 'bot6244362983:AAHZ_4fnnOULSSyIejbHKgVV6l2ujOuX6qw'
user_id = '-1001928466457'

# Load the list of product URLs from the file
with open('products.txt', 'r') as f:
    products = [line.strip().split(':') for line in f.readlines()]

print(products)

# Loop continuously and check for price changes every 5 minutes
while True:
    for product in products:
        variant_id = parse_qs(urlparse(product[1]).query)['navkey'][0]
        response = requests.get(product[1])
        soup = BeautifulSoup(response.text, 'html.parser')
        product_name = soup.find('h1', {'class': 'product-title'}).text.strip()
        old_price = soup.find('span', {'class': 'price'}).text.strip()
        new_price = soup.find('span', {'class': 'final-price'}).text.strip()
        if old_price != new_price:
            message = f"Price change for {product[0]} - {product_name}\nVariant ID: {variant_id}\nOld price: {old_price}\nNew price: {new_price}"
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage?chat_id={user_id}&text={message}"
            requests.get(url)
    time.sleep(300)  # Wait for 5 minutes before checking again


