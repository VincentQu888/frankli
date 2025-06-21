from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
import os 
import time
headers={
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3"
}
sample_company = "Google"
standard_urls = {
    "Google": "https://www.google.com/search?q={}",
    "Facebook": "https://www.facebook.com/search/top?q={}",
    "Twitter": "https://twitter.com/search?q={}" ,
    "LinkedIn": "https://www.linkedin.com/search/results/people/?keywords={}",
    "Linkedin_Company": "https://www.linkedin.com/company/{}",
}


#------------------------------SETTING UP SELENIUM WEBDRIVER TO ACCESS LINKEDIN--------------------------------

#- the email and password to be used are the ones the individual chooses to use when scrapping or uses as a means of communication.

#create webdriver isntance
driver = webdriver.Edge()

driver.get("https://linkedin.com/uas/login")

time.sleep(2)
#to load da page

#fill in the username and password with the username and password they used to login
username = driver.find_element(By.ID, "username")
username.send_keys("yovyosy869@qmail.edu.pl")
password = driver.find_element(By.ID, "password")
password.send_keys("6384u6q7")
#click the login button

driver.find_element(By.XPATH, "//button[@type='submit']").click()
# wait for the page to load
time.sleep(2)
#------------------------------END OF SETTING UP SELENIUM WEBDRIVER TO ACCESS LINKEDIN--------------------------------

#----Accessing company search results from Google, Facebook, Twitter, and LinkedIn ----##
dummy_company = "Google"  # Replace with the company you want to search for

driver.get(standard_urls["Linkedin_Company"].format(dummy_company))

#--------------Now on the company page, we can scrape data like the latest news, posts, and other relevant information----------------
src = driver.page_source

soup = BeautifulSoup(src,'lxml')
#lxml is just better, but u gotta install it 
# print(soup)  # Print the formatted HTML content
# The following line tries to find the next occurrence of the tag "lt-line-clamp__raw-line" in the parsed HTML.
# However, "lt-line-clamp__raw-line" looks like a class name, not a tag name.
# If you want to find an element with this class, use soup.find(class_="lt-line-clamp__raw-line") instead.

cheese = soup.find(class_="lt-line-clamp__raw-line")
print(cheese.text)  # Print the text content of the found element
def get_search_results(company_name):

    # if company_name not in standard_urls:
    #     raise ValueError(f"No standard URL found for {company_name}")

    url = standard_urls[company_name].format(company_name)
    response = requests.get(url, headers=headers)

    if response.status_code != 200:
        raise Exception(f"Failed to fetch data from {url}")

    soup = BeautifulSoup(response.text, 'html.parser')
    results = []



#---------------------Datascraping Linkedin Profiles-----------------------------------------------------#


    for tag in ['h3', 'h2', 'h4', 'span', 'p', 'a']:


        for item in soup.find_all(tag):
            text = item.get_text(strip=True)
            if text and text not in results:
                results.append(text)

            responses = requests.get(item.get(href,))

    return results