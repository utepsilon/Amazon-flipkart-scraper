import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse, parse_qs
import time
import pymongo


myclient = pymongo.MongoClient("mongodb://localhost:27017/")
mydb = myclient["discounts"]
mycol = mydb["discountAmazon"]


bot_token = '5420527489:AAE1F1DDhqaiUHCu-kHauFfqhgEhOlG0aMI'
user_id = '-869702003'


with open('urls.txt', 'r') as f:
    products = [ line for line in f.readlines()]


HEADERS = ({'User-Agent':
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
            'Accept-Language': 'en-US, en;q=0.5'})
            
cookies = {'session': '17ab96bd8ffbe8ca58a78657a918558'}
for product in products:
    response = requests.get(product, headers=HEADERS)
    soup = BeautifulSoup(response.text, 'html.parser')
    try:
        price =  soup.find('span',{'class':"a-price-whole"}).text.strip()
        productName = soup.find('span',{'id':"productTitle"}).text.strip()
        url1 = product.replace("?","/")
        listU = [x for x in url1.strip().split('/')]
        asin = ''
        print(productName+ " " +price)
    except:
        print("product not found : "+ str(response.status_code))
    for i in range(len(listU)):
        if(listU[i] =='dp'):
            asin = listU[i+1]
    try:            
        myquery = { "asin": asin}
        if mycol.count_documents({'asin': asin})> 0:
            mydoc = mycol.find(myquery)
            for x in mydoc:
                oldPrice = x.get("price")
                newPrice = price.replace(',','')
                newPrice = newPrice.replace('.','')
                newPrice = int(newPrice)
                if oldPrice > newPrice:
                    x["price"] = newPrice
                    mycol.update_one({"asin":asin},{ "$set": { "price": newPrice } })
                    discount = ((oldPrice - newPrice)/oldPrice) * 100
                    message = "Discount on Product : " + productName+ "\n"+ "Price : "+  "₹" +str(newPrice)+"\n"+ "Old-Price : "+'₹'+str(oldPrice) + "\n" + "\n"+"Discount :"+ str(int(discount))+"%"+ "\n"+"link : "+ str(product) 
                    url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+user_id+"&text="+message
                    if discount> 15:
                        requests.get(url)
                if oldPrice != newPrice:
                    mycol.update_one({"asin":asin},{ "$set": { "price": newPrice } })
                
                            
        else:
            newPrice = price.replace(',','')
            newPrice = newPrice.replace('.','')
            newPrice = int(newPrice)
            mydict = { "asin": asin, "price": newPrice,  "productName" : productName }
            message = "New Product Added to the list : " +productName+ "\n"+ "Price : "+ str(newPrice )+"\n"+ "\n" + "link : "+ str(product)
            x = mycol.insert_one(mydict)
            url = "https://api.telegram.org/bot"+bot_token+"/sendMessage?chat_id="+user_id+"&text="+message
            requests.get(url)
    except:
         print("product not found");
    
