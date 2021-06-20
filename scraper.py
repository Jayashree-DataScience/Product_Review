import pandas as pd
from bs4 import BeautifulSoup
from time import sleep
from selenium import webdriver
import sqlite3 as sql


headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36'}


urls = []
product_urls = []
list_of_reviews = []

# Fetch url of 250 pages
for i in range(1,251):
    urls.append(f"https://www.etsy.com/in-en/c/jewelry/earrings/ear-jackets-and-climbers?ref=pagination&explicit=1&page={i}")

"""
Visit each page of ear-jackets and climbers and scrape 65 product url links in each page """
for url in urls:
    driver1=webdriver.Chrome(executable_path='C:/Users/Jhv/Downloads/chromedriver_win32(1)/chromedriver.exe')
    driver1.get(url)
    sleep(5)
    for i in range(1, 65):
        product = driver1.find_element_by_xpath("//div[@id='content']//div[contains(@class,'search-listings-group')]//ul//li['"+str(i)+"']/div/a")
        product_urls.append(product.get_attribute('href'))

driver=webdriver.Firefox(executable_path='C:/Users/Jhv/Downloads/geckodriver-v0.29.1-win64/geckodriver.exe')


""" product links are visited to fetch reviews"""
for product_url in product_urls:
    try:
        driver.get(product_url)
        sleep(5)
        html = driver.page_source
        soup = BeautifulSoup(html,'html')
        for i in range(4):
            try:
                list_of_reviews.append(soup.select(f'#review-preview-toggle-{i}')[0].getText().strip())
            except:
                continue
        while(True):
            try:
                next_button = driver.find_element_by_xpath('//*[@id="reviews"]/div[2]/nav/ul/li[position() = last()]/a[contains(@href, "https")]')
                if next_button != None:
                    next_button.click()
                    sleep(5)
                    html = driver.page_source
                    soup = BeautifulSoup(html,'html')
                    for i in range(6):
                        try: 
                            list_of_reviews.append(soup.select(f'#review-preview-toggle-{i}')[0].getText().strip())
                        except:
                            continue
            except Exception as e:
                print('finsish : ', e)
                break
    except:
        continue
    
scrapedReviewsAll = pd.DataFrame(list_of_reviews, index = None, columns = ['reviews'])         
scrapedReviewsAll.to_csv('C:/JaY_personal/Forsk/project15/scraped_Reviews_etsyfull1.csv')
df = pd.read_csv('C:/JaY_personal/Forsk/project15/scraped_Reviews_etsyfull1.csv')
conn = sql.connect('C:/JaY_personal/Forsk/project15/scraped_Reviews_etsyfull1.db')
df.to_sql('C:/JaY_personal/Forsk/project15/scraped_ReviewsTable_etsyfull1', conn)    
print(len(list_of_reviews))
print(len(product_urls))
urls_df=pd.DataFrame(urls,index=None)
urls_df.to_csv('C:/JaY_personal/Forsk/Scrapers/urls.csv')
product_urls_df=pd.DataFrame(product_urls,index=None)
product_urls_df.to_csv('C:/JaY_personal/Forsk/Scrapers/product_urls.csv')

driver.close()
driver.quit()

