from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
import time
import random
from urllib.parse import urljoin, urlparse

from config import (
    SCRAPING_DELAY,
    MAX_PAGES_PER_SITE,
    EXCLUDED_EXTENSIONS,
    EXCLUDED_DOMAINS
)

#  Helpers


def get_domain(url):
    domain = urlparse(url).netloc.lower()
    if domain.startswith("www."):
        domain = domain.replace("www.", "")
    return domain


def is_valid_link(link):
    link = link.lower()

    if any(ext in link for ext in EXCLUDED_EXTENSIONS):
        return False

    if any(domain in link for domain in EXCLUDED_DOMAINS):
        return False

    return True


def is_external_link(source, target):
    return get_domain(source) != get_domain(target)

#  Driver


def get_driver():
    options = Options()
    options.add_argument("--headless=new")  
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-blink-features=AutomationControlled")

    return webdriver.Chrome(
        service=Service(ChromeDriverManager().install()),
        options=options
    )

# Scrape Page


def scrape_dynamic_page(driver, url: str):
    try:
        driver.get(url)
        time.sleep(3)

        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"
        links = set()

        elements = driver.find_elements(By.TAG_NAME, "a")

        for el in elements:
            href = el.get_attribute("href")

            if not href:
                continue

            if href.startswith("http"):
                full_link = href
            elif href.startswith("/"):
                full_link = urljoin(base, href)
            else:
                continue

            if not is_valid_link(full_link):
                continue

            if not is_external_link(url, full_link):
                continue

            links.add(full_link)

        #  HTML → texte
        soup = BeautifulSoup(driver.page_source, "lxml")

        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()

        text = soup.get_text(separator=" ", strip=True)

      
        if "politique" in text.lower():
            label = "fake"
        else:
            label = "real"

        time.sleep(SCRAPING_DELAY)

        return {
            "url": url,
            "domain": get_domain(url),
            "title": driver.title.strip() if driver.title else "",
            "text": text[:5000],
            "label": label, 
            "links": list(links),
            "nb_links": len(links),
            "scraped_at": time.time()
        }

    except Exception as e:
        print(f"[SELENIUM ERROR] {url} : {e}")
        return None

#  Dynamic Crawler


def crawl_dynamic_site(start_url: str, max_pages=MAX_PAGES_PER_SITE):
    driver = get_driver()

    visited = set()
    to_visit = [start_url]
    results = []

    try:
        while to_visit and len(results) < max_pages:
            url = to_visit.pop(0)

            if url in visited:
                continue

            print(f"[DYNAMIC CRAWL] {len(results)+1}/{max_pages} → {url}")

            data = scrape_dynamic_page(driver, url)

            if not data:
                continue

            visited.add(url)
            results.append(data)

            # ajout nouveaux liens
            for link in data["links"]:
                if link not in visited and len(to_visit) < max_pages:
                    to_visit.append(link)

    finally:
        driver.quit()

    return results


#  Multiple Sites


def scrape_dynamic_multiple(sites: list):
    all_results = []

    for site in sites:
        print(f"\n[DYNAMIC SITE] {site}")
        site_data = crawl_dynamic_site(site)
        all_results.extend(site_data)

    return all_results