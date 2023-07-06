import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time
import pymongo

myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["flipdiscounts"]
mycol = mydb["flipdiscount"]


bot_token = '5420527489:AAE1F1DDhqaiUHCu-kHauFfqhgEhOlG0aMI'
user_id = '-869702003'


HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})


with open('Flipkarturls.txt', 'r') as f:
    products = [ line for line in f.readlines()]
    
with open('output_flipkart_url.txt','w') as outfile:
    for product in products:
        response = requests.get(product,headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        try:
            urls =  list()
            for i in soup.find_all('a', {'class': '_1fQZEK'}):
                urls.append("https://www.flipkart.com"+i.get('href'))
            for i in soup.find_all('a', {'class': '_2rpwqI'}):
                urls.append("https://www.flipkart.com"+i.get('href'))    
            print(urls)
            for i in urls:
                outfile.write(i)
                outfile.write("\n")
        except:
            print("failed")