import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time

bot_token = '5420527489:AAE1F1DDhqaiUHCu-kHauFfqhgEhOlG0aMI'
user_id = '-869702003'


with open('discount.txt', 'r') as f:
    products = [ line.split('@') for line in f.readlines()]

print(products)


for product in products:
    finaldiscount = int(product[0])
    response = requests.get(product[1])
    soup = BeautifulSoup(response.text, 'html.parser')
    productNames = []
    price = []
    link = []
    discount = []
        #print(soup)
    for i in soup.find_all('a', {'class': 'plp-card-wrapper plp_product_list'}):
        productNames.append(i.get('title'))
        link.append('https://www.jiomart.com'+i.get('href'))
        #print(link)
    for i in soup.find_all('span', {'class': 'jm-heading-xxs jm-mb-xxs'}):
        price.append(i.text.strip())
        #print(price)
    for i in soup.find_all('span', {'class': 'jm-badge'}):
        discount.append(i.text.strip())
      
    print(len(discount),len(price),len(productNames),len(link),end =" ")
    print(productNames)
    for i in range(len(discount)):
        li = discount[i].split('%')
        print(li[0])
        if(int(li[0]) >= finaldiscount):
            message = "Discount on Product : " + productNames[i]+ "\n"+ "Price : "+price[i]+ "\n"+ "Discount : "+discount[i] +"\n" + "link : "+ link[i];
            url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+user_id+"&text="+message
            print(message)
            requests.get(url)
