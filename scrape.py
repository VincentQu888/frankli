from selenium import webdriver
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
import json
import time
import sys
import io

# Fix encoding for Unicode output
if hasattr(sys.stdout, 'buffer'):
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

STANDARD_URLS = {
    "Linkedin_Company": "https://www.linkedin.com/company/{}",
    "Linkedin_Posts": "https://www.linkedin.com/company/{}/posts/",
    "Linkedin_Overview": "https://www.linkedin.com/company/{}/about/"
}

def setup_driver():
    return webdriver.Edge()

def login_linkedin(driver, email, password):
    driver.get("https://linkedin.com/uas/login")
    time.sleep(2)
    driver.find_element(By.ID, "username").send_keys(email)
    driver.find_element(By.ID, "password").send_keys(password)
    driver.find_element(By.XPATH, "//button[@type='submit']").click()
    time.sleep(3)

def scrape_company_profile(driver, company_name):
    driver.get(STANDARD_URLS["Linkedin_Company"].format(company_name))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    main_div = soup.find("div", class_="org-top-card__primary-content")
    if not main_div:
        return {
                "company_name": 'test',
                "logo_url": 'test',
                "industry": 'test',
                "location": 'test',
                "followers": 'test',
                "employees": 'test',
            }

    profile = {
        "company_name": main_div.find("h1", class_="org-top-card-summary__title").get_text(strip=True) if main_div.find("h1") else None,
        "logo_url": main_div.find("img")["src"] if main_div.find("img") else None,
        "industry": None,
        "location": None,
        "followers": None,
        "employees": None,
        "website_url": None,
    }

    info_items = main_div.select("div.org-top-card-summary-info-list__info-item")
    for item in info_items:
        text = item.get_text(strip=True).lower()
        if "followers" in text:
            profile["followers"] = text
        elif "," in text:
            profile["location"] = text
        else:
            profile["industry"] = text

    employee_tag = main_div.find("a", class_="org-top-card-summary-info-list__info-item-link")
    if employee_tag:
        profile["employees"] = employee_tag.get_text(strip=True)

    website_btn = soup.find("a", string=lambda s: s and "Visit website" in s)
    if website_btn:
        profile["website_url"] = website_btn['href']

    return profile

def scrape_company_posts(driver, company_name):
    driver.get(STANDARD_URLS["Linkedin_Posts"].format(company_name))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    posts = []
    for item in soup.find_all("span", dir="ltr"):
        text = item.get_text(strip=True)
        if text:
            posts.append(text)

    return {"recent_posts": posts}

def scrape_company_overview(driver, company_name):
    driver.get(STANDARD_URLS["Linkedin_Overview"].format(company_name))
    time.sleep(2)
    soup = BeautifulSoup(driver.page_source, 'lxml')

    overview = soup.find("p", class_="break-words white-space-pre-wrap t-black--light text-body-medium")
    if overview:
        return overview.get_text(strip=True)
    return "Overview not found"

def run_scraper_api(company_name, email, password):
    driver = setup_driver()
    try:
        login_linkedin(driver, email, password)
        profile = scrape_company_profile(driver, company_name)
        posts = scrape_company_posts(driver, company_name)
        overview = scrape_company_overview(driver, company_name)
        
        data = {
            "company": company_name,
            "profile": profile,
            "overview": overview,
            "posts": posts["recent_posts"]
        }

        return data
    finally:
        driver.quit()



# # Example usage (to test locally):
# if __name__ == "__main__":
#     email = ""
#     password = ""
#     company = "amazon"
# # test the shit here
#     data = run_scraper_api(company, email, password)
#     print(json.dumps(data, indent=2, ensure_ascii=False))
