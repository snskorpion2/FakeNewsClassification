import requests
from bs4 import BeautifulSoup
import re
import time
import os
import csv

BASE_URL = "https://www.forbes.com"
START_URL = BASE_URL + "/"
# Match both full and relative URLs for Forbes articles
ART_PATTERN = re.compile(r"^(?:https?://www\.forbes\.com)?/sites/[A-Za-z0-9_-]+/\d{4}/\d{2}/\d{2}/.*$")
CSV_FILE = 'forbes_articles.csv'
CSV_DELIMITER = ';'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; ForbesScraper/1.0; +https://example.com/bot)'
}


def fetch_soup(url):
    """Fetches a URL and returns a BeautifulSoup object"""
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def find_article_links(soup):
    """Find all article links on the page matching our pattern"""
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href'].split('?')[0]
        if ART_PATTERN.match(href):
            if href.startswith('http'):
                links.add(href)
            else:
                links.add(BASE_URL + href)
    return links


def scrape_article(url):
    """Scrape title and main text from a Forbes article URL"""
    soup = fetch_soup(url)

    # Title inside <main> ... <h1>
    title_tag = soup.select_one('main h1')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Main text: paragraphs within a div whose class contains 'article-body-container'
    body_div = None
    for div in soup.find_all('div', class_=True):
        if 'article-body-container' in ' '.join(div.get('class')):
            body_div = div
            break

    paragraphs = []
    if body_div:
        for p in body_div.find_all('p'):
            text = p.get_text()
            if text:
                paragraphs.append(text)
    content = '\n\n'.join(paragraphs)

    return {
        'url': url,
        'title': title,
        'content': content
    }


def load_scraped_urls():
    """Load previously scraped URLs from the CSV"""
    if not os.path.exists(CSV_FILE):
        return set()
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=CSV_DELIMITER)
        return {row['url'] for row in reader}


def save_article(article):
    """Append an article record to the CSV file"""
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(
            f,
            fieldnames=['url', 'title', 'content'],
            delimiter=CSV_DELIMITER,
            quoting=csv.QUOTE_MINIMAL
        )
        if not file_exists:
            writer.writeheader()
        writer.writerow(article)


def main():
    print(f"Fetching start page: {START_URL}")
    soup = fetch_soup(START_URL)

    article_links = find_article_links(soup)
    print(f"Found {len(article_links)} article links.")

    scraped = load_scraped_urls()
    print(f"Already have {len(scraped)} articles; will skip duplicates.")

    for idx, url in enumerate(sorted(article_links), start=1):
        if url in scraped:
            print(f"[{idx}/{len(article_links)}] Skipping: {url}")
            continue
        try:
            print(f"[{idx}/{len(article_links)}] Scraping: {url}")
            art = scrape_article(url)
            save_article(art)
            scraped.add(url)
            time.sleep(1)
        except Exception as e:
            print(f"Error scraping {url}: {e}")

    print("Done. Articles appended to forbes_articles.csv")

if __name__ == '__main__':
    main()
