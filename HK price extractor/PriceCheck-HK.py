import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time
import pymongo
myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["hkprice"]
mycol = mydb["price"]


bot_token = '6288451570:AAEi2DQpUE9D7LMI71WftcgDhPwV8GON3yw'
user_id = '-826162444'



with open('products.txt', 'r') as f:
    products = [line.strip().split('@') for line in f.readlines()]
    
#response = requests.get("https://www.healthkart.com/sv/gat-l-arginine/SP-42820?navKey=VRNT-77583")
#soup = BeautifulSoup(response.text, 'html.parser')

while True:
    for product in products:
        response = requests.get(product[1])
        variantId = parse_qs(urlparse(product[1]).query)['navKey'][0]
        soup = BeautifulSoup(response.text, 'html.parser')
        newPrice = soup.find('span', {'class': 'price-value-value variantInfo_price-value-value__2ZQIC'}).text.strip()
        productName = soup.find('h1', {'class': 'variantInfo_var-info__nm__ZlOER'}).text.strip()
        
        key = product[0];
        myquery = { "key": key}
        if mycol.count_documents({'key': key})> 0:
            mydoc = mycol.find(myquery)
            for x in mydoc:
                oldPrice = x.get("price")
                if oldPrice != newPrice:
                    x["price"] = newPrice
                    mycol.update_one({"key":key},{ "$set": { "price": newPrice } })
                    message = "Price change for " +key +" - "+ productName+ "\nVariant ID: "+variantId +"\nOld price: "+oldPrice+"\nNew price:" +newPrice
                    #print(message)
                    print("change in price detected for product "+ key)
                    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+user_id+"&text="+message
                    #print(url)
                    requests.get(url)
        else:
            mydict = { "key": key, "price": newPrice,  "productName" : productName, "variantId":variantId }
            x = mycol.insert_one(mydict)
            #print("added to db")
    time.sleep(300)