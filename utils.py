from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import os
import time
import requests
from bs4 import BeautifulSoup
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
load_dotenv()

#---------------------------------------------------------------------------


def move_to_reviews(url):
    # driver = webdriver.Chrome(executable_path="chromedriver.exe")  
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(options=chrome_options)
    
    driver.get(f"{url}")

    WebDriverWait(driver, 40).until(
        EC.presence_of_all_elements_located((By.PARTIAL_LINK_TEXT, "件）")))

    link_element = driver.find_element(By.PARTIAL_LINK_TEXT, "件）")
    link_url = link_element.get_attribute('href').split('1.1')[0]

    time.sleep(10)
    driver.quit()

    return link_url


#---------------------------------------------------------------------------


def get_soup(link_url):
    response = requests.get(link_url)
    soup = BeautifulSoup(response.text, "html.parser")
    return soup


#---------------------------------------------------------------------------


def product_details(soup):
    total_reviews = soup.find("span", {"class": "Count"}).text.strip()
    price = soup.find("span", {"revPrice"}).text.strip()
    product = soup.find("h2", {"class": "revItemTtl"}).text.strip()
    img_tag = soup.select_one('#thumbWindow img')
    if img_tag:
        image_link = img_tag.get('src')

    details = {
        'product_name': product,
        'product_image': image_link,
        'product_price': price + '円',
        'total_reviews': total_reviews
    }

    return details


#---------------------------------------------------------------------------


def page_jumper(url_link, num_pages=0):
    soup = get_soup(url_link)
    total_reviews = int(soup.find("span", {"class": "Count"}).text.strip().replace(',', ''))

    total_pages = int(total_reviews)/15
    pages = num_pages

    link_list = []
    if pages <= total_pages:
        for i in range(pages):
            link_list.append(f"{url_link}{i+1}.1/")
        return link_list
    elif pages > total_pages:
        return f"Total number of pages are {total_pages}. Please enter a value equal or below total number of pages"
    else:
        return "Number of pages doesn't exist"
    

#---------------------------------------------------------------------------


def product_reviews(link_list):
    reviewlist = []
    
    for link in link_list:
        soup = get_soup(link)
        reviews = soup.find_all("div", {"class": "revRvwUserSec"})
        
        for item in reviews:
            review = {
            'rating': float(item.find("span", {"class":"revUserRvwerNum"}).text.strip()),
            'date': item.find("span", {"class":"revUserEntryDate"}).text.strip(),
            'body': item.find("dd", {"class":"revRvwUserEntryCmt"}).text.strip(),
            }
            reviewlist.append(review)
    return reviewlist


#---------------------------------------------------------------------------


def convert_to_df(reviews):
    df_reviews = pd.DataFrame(reviews)
    descriptions = df_reviews['body']
    return descriptions


#---------------------------------------------------------------------------


def sentiment(descriptions):
    client = Groq(
        api_key=os.getenv("GROQ_API_KEY"),
    )

    chat_completion = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"Analyzing the {descriptions} give me the general sentiment regarding the product and suggestions for how to imporve the product, increase the sales and get better reviews",
            }
        ],
        model="llama3-70b-8192",
    )
    return chat_completion.choices[0].message.content