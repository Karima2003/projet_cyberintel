import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
import urllib.robotparser
import time
import random
from urllib.parse import urljoin, urlparse

from config import (
    SCRAPING_DELAY,
    RESPECT_ROBOTS,
    TIMEOUT,
    MAX_PAGES_PER_SITE,
    EXCLUDED_EXTENSIONS,
    EXCLUDED_DOMAINS
)

ua = UserAgent()

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



#  Robots.txt


def can_fetch(url: str) -> bool:
    try:
        parsed = urlparse(url)
        robots_url = f"{parsed.scheme}://{parsed.netloc}/robots.txt"
        rp = urllib.robotparser.RobotFileParser()
        rp.set_url(robots_url)
        rp.read()
        return rp.can_fetch("*", url)
    except:
        return True



#  Scrape Page


def scrape_page(url: str):

    if RESPECT_ROBOTS and not can_fetch(url):
        print(f"[SKIP] robots.txt : {url}")
        return None

    headers = {
        "User-Agent": ua.random,
        "Accept-Language": "fr,en;q=0.8"
    }

    try:
        resp = requests.get(url, headers=headers, timeout=TIMEOUT)
        resp.raise_for_status()

        soup = BeautifulSoup(resp.text, "lxml")

        base = f"{urlparse(url).scheme}://{urlparse(url).netloc}"

        links = set()

        for a in soup.find_all("a", href=True):
            href = a["href"]

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

        #  nettoyage HTML
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
            "title": soup.title.string.strip() if soup.title else "",
            "text": text[:5000],
            "label": label, 
            "links": list(links),
            "nb_links": len(links),
            "status_code": resp.status_code,
            "scraped_at": time.time()
        }

    except Exception as e:
        print(f"[ERROR] {url} : {e}")
        return None


#  Crawler


def crawl_site(start_url: str, max_pages=MAX_PAGES_PER_SITE):
    visited = set()
    to_visit = [start_url]
    results = []

    while to_visit and len(results) < max_pages:
        url = to_visit.pop(0)

        if url in visited:
            continue

        print(f"[CRAWL] {len(results)+1}/{max_pages} → {url}")

        data = scrape_page(url)

        if not data:
            continue

        visited.add(url)
        results.append(data)

        #  ajout nouveaux liens
        for link in data["links"]:
            if link not in visited and len(to_visit) < max_pages:
                to_visit.append(link)

    return results


# Scrape Multiple Sites


def scrape_multiple(sites: list):
    all_results = []

    for site in sites:
        print(f"\n[SITE] {site}")
        site_data = crawl_site(site)
        all_results.extend(site_data)

    return all_results