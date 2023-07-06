import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

bot_token = '6288451570:AAEi2DQpUE9D7LMI71WftcgDhPwV8GON3yw'
user_id = '-885787951'

with open('discount.txt', 'r') as f:
    products = [ line for line in f.readlines()]

print(products)

while True:
    for product in products:
        response = requests.get(product)
        soup = BeautifulSoup(response.text, 'html.parser')
        productNames = []
        price = []
        link = []
        discount = []
        for i in soup.find_all('div', {'class': 'variant-name variantBoxDesktopLayoutLoyal_variant-name__15TPT'}):
            productNames.append(i.text.strip())
    #print(productNames)

        for i in soup.find_all('a', {'class': 'variant-img-container relative variantBoxDesktopLayoutLoyal_variant-img-container__1ZE7P'}):
            link.append("https://www.healthkart.com"+i.get('href'))
    #print(link)
        for i in soup.find_all('span', {'class': 'variant-price variantBoxDesktopLayoutLoyal_variant-price__36JaH'}):
            price.append(i.text.strip())
        print(price)
        for i in soup.find_all('span', {'class': 'variant-offer variantBoxDesktopLayoutLoyal_variant-offer__1t4IA'}):
            discount.append(i.text.strip())
        

        for i in range(len(productNames)):
            message = "Discount on Product : " + productNames[i]+ "\n"+ "Price : "+price[i]+ "\n"+ "Discount : "+discount[i] +"\n" + "link : "+ link[i];
            url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+user_id+"&text="+message
            requests.get(url)
    time.sleep(300)
