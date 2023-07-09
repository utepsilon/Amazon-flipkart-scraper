import asyncio
# Import necessary libraries
import re
import random
import datetime
import pandas as pd
from playwright.async_api import async_playwright


async def get_sale_price(page):
    try:
        # Get sale price element and extract text content
        sale_price_element = await page.query_selector(".a-price-whole")
        sale_price = await sale_price_element.text_content()
    except:
        # Set sale price to "Not Available" if element not found or text content cannot be extracted
        sale_price = "Not Available"
    return sale_price

async def get_MRP(page):
    try:
        # Get MRP element and extract text content
        MRP_element = await page.query_selector(".a-price.a-text-price")
        MRP = await MRP_element.text_content()
        MRP = MRP.split("₹")[1]
    except:
        # Set MRP to "Not Available" if element not found or text content cannot be extracted
        MRP = "Not Available"
    return MRP


async def get_num_reviews(page):
    try:
        # Find the number of reviews element and get its text content
        num_reviews_elem = await page.query_selector("#acrCustomerReviewLink #acrCustomerReviewText")
        num_reviews = await num_ratings_elem.inner_text()
        num_reviews = num_ratings.split(" ")[0]
    except:
        try:
            # If the previous attempt failed, check if there are no reviews for the product
            no_review_elem = await page.query_selector("#averageCustomerReviews #acrNoReviewText")
            num_reviews = await no_review_elem.inner_text()
        except:
            # If all attempts fail, set the number of reviews as "Not Available"
            num_reviews = "Not Available"

    # Return the number of reviews
    return num_reviews

async def get_best_sellers_rank(page):
    try:
        # Try to get the Best Sellers Rank element
        best_sellers_rank = await (await page.query_selector("tr th:has-text('Best Sellers Rank') + td")).text_content()

        # Split the rank string into individual ranks
        ranks = best_sellers_rank.split("#")[1:]

        # Initialize the home & kitchen and air fryers rank variables
        home_kitchen_rank = ""
        air_fryers_rank = ""

        # Loop through each rank and assign the corresponding rank to the appropriate variable
        for rank in ranks:
            if "in Home & Kitchen" in rank:
                home_kitchen_rank = rank.split(" ")[0].replace(",", "")
            elif "in Air Fryers" or "in Deep Fat Fryers" in rank:
                air_fryers_rank = rank.split(" ")[0].replace(",", "")
    except:
        # If the Best Sellers Rank element is not found, assign "Not Available" to both variables
        home_kitchen_rank = "Not Available"
        air_fryers_rank = "Not Available"

    # Return the home & kitchen and air fryers rank values
    return home_kitchen_rank, air_fryers_rank

async def get_brand_name(page):
    try:
        # Find the brand name element and get its text content
        brand_name_elem = await page.query_selector('#bylineInfo_feature_div .a-link-normal')
        brand_name = await brand_name_elem.text_content()

        # Remove any unwanted text from the brand name using regular expressions
        brand_name = re.sub(r'Visit|the|Store|Brand:', '', brand_name).strip()
    except:
        # If an exception occurs, set the brand name as "Not Available"
        brand_name = "Not Available"

    # Return the cleaned up brand name
    return brand_name

async def get_star_rating(page):
    try:
        # Find the star rating element and get its text content
        star_rating_elem = await page.wait_for_selector(".a-icon-alt")
        star_rating = await star_rating_elem.inner_text()
        star_rating = star_rating.split(" ")[0]
    except:
        try:
            # If the previous attempt failed, check if there are no reviews for the product
            star_ratings_elem = await page.query_selector("#averageCustomerReviews #acrNoReviewText")
            star_rating = await star_ratings_elem.inner_text()
        except:
            # If all attempts fail, set the star rating as "Not Available"
            star_rating = "Not Available"

    # Return the star rating
    return star_rating


async def get_product_name(page):
    try:
        # Find the product title element and get its text content
        product_name_elem = await page.query_selector("#productTitle")
        product_name = await product_name_elem.text_content()
    except:
        # If an exception occurs, set the product name as "Not Available"
        product_name = "Not Available"

    # Remove any leading/trailing whitespace from the product name and return it
    return product_name.strip()

async def get_product_urls(browser, page):
    # Select all elements with the product urls
    all_items = await page.query_selector_all('.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
    product_urls = set()
    # Loop through each item and extract the href attribute
    for item in all_items:
        url = await item.get_attribute('href')
        # If the link contains '/ref' 
        if '/ref' in url:
            # Extract the base URL
            full_url = 'https://www.amazon.in' + url.split("/ref")[0]
        # If the link contains '/sspa/click?ie'
        elif '/sspa/click?ie' in url:
            # Extract the product ID and clean the URL
            product_id = url.split('%2Fref%')[0]
            clean_url = product_id.replace("%2Fdp%2F", "/dp/")
            urls = clean_url.split('url=%2F')[1]
            full_url = 'https://www.amazon.in/' + urls
        # If the link doesn't contain either '/sspa/click?ie' or '/ref'
        else:
            # Use the original URL
            full_url = 'https://www.amazon.in' + url

        if not any(substring in full_url for substring in ['Basket', 'Accessories', 'accessories', 'Disposable', 'Paper', 'Reusable', 'Steamer', 'Silicone', 'Liners', 'Vegetable-Preparation', 'Pan', 'parchment', 'Parchment', 'Cutter', 'Tray', 'Cheat-Sheet', 'Reference-Various', 'Cover', 'Crisper', 'Replacement']):
            product_urls.add(full_url)
            # Use add instead of append to prevent duplicates

    # Check if there is a next button
    next_button = await page.query_selector("a.s-pagination-item.s-pagination-next.s-pagination-button.s-pagination-separator")
    if next_button:
        # If there is a next button, click on it
        is_button_clickable = await next_button.is_enabled()
        if is_button_clickable:
            await next_button.click()
            # Wait for the next page to load
            await page.wait_for_selector('.a-link-normal.s-underline-text.s-underline-link-text.s-link-style.a-text-normal')
            # Recursively call the function to extract links from the next page
            product_urls.update(await get_product_urls(browser, page))  
        else:
            print("Next button is not clickable")  

    num_products = len(product_urls)
    print(f"Scraped {num_products} products.")

    return list(product_urls)

async def get_technical_details(page):
    try:
        # Get table containing technical details and its rows
        table_element = await page.query_selector("#productDetails_techSpec_section_1")
        rows = await table_element.query_selector_all("tr")

        # Initialize dictionary to store technical details
        technical_details = {}

        # Iterate over rows and extract key-value pairs
        for row in rows:
            # Get key and value elements for each row
            key_element = await row.query_selector("th")
            value_element = await row.query_selector("td")

            # Extract text content of key and value elements
            key = await page.evaluate('(element) => element.textContent', key_element)
            value = await page.evaluate('(element) => element.textContent', value_element)

            # Strip whitespace and unwanted characters from value and add key-value pair to dictionary
            value = value.strip().replace('\u200e', '')
            technical_details[key.strip()] = value

        # Extract required technical details (colour, capacity, wattage, country of origin)
        colour = technical_details.get('Colour', 'Not Available')
        if colour == 'Not Available':
            # Get the colour element from the page and extract its inner text
            colour_element = await page.query_selector('.po-color .a-span9')
            if colour_element:
                colour = await colour_element.inner_text()
                colour = colour.strip()

        capacity = technical_details.get('Capacity', 'Not Available')
        if capacity == 'Not Available' or capacity == 'default':
            # Get the capacity element from the page and extract its inner text
            capacity_element = await page.query_selector('.po-capacity .a-span9')
            if capacity_element:
                capacity = await capacity_element.inner_text()
                capacity = capacity.strip()

        wattage = technical_details.get('Wattage', 'Not Available')
        if wattage == 'Not Available' or wattage == 'default':
            # Get the wattage element from the page and extract its inner text
            wattage_elem = await page.query_selector('.po-wattage .a-span9')
            if wattage_elem:
                wattage = await wattage_elem.inner_text()
                wattage = wattage.strip()

        country_of_origin = technical_details.get('Country of Origin', 'Not Available')

        # Return technical details and required fields
        return technical_details, colour, capacity, wattage, country_of_origin

    except:
        # Set technical details to default values if table element or any required element is not found or text content cannot be extracted
        return {}, 'Not Available', 'Not Available', 'Not Available', 'Not Available'
async def get_bullet_points(page):
    bullet_points = []
    try:
        # Try to get the unordered list element containing the bullet points
        ul_element = await page.query_selector('#feature-bullets ul.a-vertical')

        # Get all the list item elements under the unordered list element
        li_elements = await ul_element.query_selector_all('li')

        # Loop through each list item element and append the inner text to the bullet points list
        for li in li_elements:
            bullet_points.append(await li.inner_text())
    except:
        # If the unordered list element or list item elements are not found, assign an empty list to bullet points
        bullet_points = []

    # Return the list of bullet points
    return bullet_points


async def perform_request_with_retry(page, url):
    # set maximum retries
    MAX_RETRIES = 5
    # initialize retry counter
    retry_count = 0

    # loop until maximum retries are reached
    while retry_count < MAX_RETRIES:
        try:
            # try to make request to the URL using the page object and a timeout of 30 seconds
            await page.goto(url, timeout=80000)
            # break out of the loop if the request was successful
            break
        except:
            # if an exception occurs, increment the retry counter
            retry_count += 1
            # if maximum retries have been reached, raise an exception
            if retry_count == MAX_RETRIES:
                raise Exception("Request timed out")
            # wait for a random amount of time between 1 and 5 seconds before retrying
            await asyncio.sleep(random.uniform(1, 5))
async def main():
    # Launch a Firefox browser using Playwright
    async with async_playwright() as pw:
        browser = await pw.firefox.launch()
        page = await browser.new_page()

        # Make a request to the Amazon search page and extract the product URLs
        await perform_request_with_retry(page, 'https://www.amazon.in/s?k=laptop')
        product_urls = await get_product_urls(browser, page)
        data = []
        j = 1
        # Loop through each product URL and scrape the necessary information
        for i, url in enumerate(product_urls):
            await perform_request_with_retry(page, url)

            product_name = await get_product_name(page)
            brand = await get_brand_name(page)
            star_rating = await get_star_rating(page)
            num_reviews = await get_num_reviews(page)
            MRP = await get_MRP(page)
            sale_price = await get_sale_price(page)
            home_kitchen_rank, air_fryers_rank = await get_best_sellers_rank(page)
            technical_details, colour, capacity, wattage, country_of_origin = await get_technical_details(page)
            bullet_points = await get_bullet_points(page)

            # Print progress message after processing every 10 product URLs
            if i % 10 == 0 and i > 0:
                print(f"Processed {i} links.")

            # Print completion message after all product URLs have been processed
            if i == len(product_urls) - 1:
                print(f"All information for url {i} has been scraped.")
            

            # Add the corresponding date
            today = datetime.datetime.now().strftime("%Y-%m-%d")
            # Add the scraped information to a list
            data.append(( today, url, product_name, brand, star_rating, num_reviews, MRP, sale_price, colour, capacity, wattage, country_of_origin, home_kitchen_rank, air_fryers_rank, technical_details, bullet_points))
            df = pd.DataFrame(data, columns=['date', 'product_url', 'product_name', 'brand', 'star_rating', 'number_of_reviews', 'MRP', 'sale_price', 'colour', 'capacity', 'wattage', 'country_of_origin', 'home_kitchen_rank', 'air_fryers_rank', 'technical_details', 'description'])
            fileName = 'product_data' + str(j)+'.csv'
            df.to_csv(fileName, index=False)
            j = j+1;
        # Convert the list of tuples to a Pandas DataFrame and save it to a CSV file
        df = pd.DataFrame(data, columns=['date', 'product_url', 'product_name', 'brand', 'star_rating', 'number_of_reviews', 'MRP', 'sale_price', 'colour', 'capacity', 'wattage', 'country_of_origin', 'home_kitchen_rank', 'air_fryers_rank', 'technical_details', 'description'])
        df.to_csv('product_data.csv', index=False)
        print('CSV file has been written successfully.')

        # Close the browser
        await browser.close()


if __name__ == '__main__':
    asyncio.run(main())