import requests
from bs4 import BeautifulSoup
import re
import time
import os
import csv

BASE_URL = "https://www.bbc.com"
START_PATH = "/news"
ART_PATTERN = re.compile(r"^/news/articles/[a-z0-9]+$")
CSV_FILE = 'bbc_news_articles.csv'
CSV_DELIMITER = ';'

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; BBCScraper/1.0; +https://example.com/bot)'
}

def fetch_page(path):
    """Fetches and returns BeautifulSoup of a given path under BASE_URL"""
    url = BASE_URL + path
    resp = requests.get(url, headers=HEADERS, timeout=10)
    resp.raise_for_status()
    return BeautifulSoup(resp.text, 'html.parser')


def find_article_paths(soup):
    """Finds all article link paths matching /news/articles/..."""
    links = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        if ART_PATTERN.match(href):
            links.add(href)
    return links


def scrape_article(path):
    """Scrapes title and content from an article path"""
    soup = fetch_page(path)

    # Title inside <main> <article> ... <h1>
    title_tag = soup.select_one('main article h1')
    title = title_tag.get_text(strip=True) if title_tag else ''

    # Content from data-component="text-block"
    paragraphs = []
    for block in soup.find_all('div', {'data-component': 'text-block'}):
        for p in block.find_all('p'):
            text = p.get_text()
            if text:
                paragraphs.append(text)
    content = '\n\n'.join(paragraphs)

    return {
        'url': BASE_URL + path,
        'title': title,
        'content': content
    }


def load_scraped_urls():
    """Loads URLs already saved in the CSV file"""
    if not os.path.exists(CSV_FILE):
        return set()
    with open(CSV_FILE, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=CSV_DELIMITER)
        return {row['url'] for row in reader}


def save_article_to_csv(article):
    """Appends a single article dict to the CSV"""
    file_exists = os.path.exists(CSV_FILE)
    with open(CSV_FILE, 'a', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f,
                                fieldnames=['url', 'title', 'content'],
                                delimiter=CSV_DELIMITER,
                                quoting=csv.QUOTE_MINIMAL)
        if not file_exists:
            writer.writeheader()
        writer.writerow(article)


def main():
    print(f"Fetching start page: {BASE_URL + START_PATH}")
    home_soup = fetch_page(START_PATH)

    article_paths = find_article_paths(home_soup)
    print(f"Discovered {len(article_paths)} article links on homepage.")

    scraped_urls = load_scraped_urls()
    print(f"Already scraped {len(scraped_urls)} articles. Skipping duplicates.")

    for i, path in enumerate(sorted(article_paths), start=1):
        full_url = BASE_URL + path
        if full_url in scraped_urls:
            print(f"[{i}/{len(article_paths)}] Skipping already scraped: {full_url}")
            continue
        try:
            print(f"[{i}/{len(article_paths)}] Scraping: {full_url}")
            art = scrape_article(path)
            save_article_to_csv(art)
            scraped_urls.add(full_url)
            time.sleep(1)  # politeness delay
        except Exception as e:
            print(f"Failed to scrape {full_url}: {e}")

    print("Done. New articles appended to bbc_news_articles.csv")

if __name__ == '__main__':
    main()
