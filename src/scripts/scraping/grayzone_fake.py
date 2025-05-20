import re
import time
import csv
import requests
from bs4 import BeautifulSoup

# Configuration
TARGET_REGEX = re.compile(r"^https://thegrayzone\.com/\d{4}/\d{2}/\d{2}/[\w\-]+/")
BASE_URL = "https://thegrayzone.com/"
PAGE_URL_TEMPLATE = "https://thegrayzone.com/page/{}/"
MAX_PAGE = 107
OUTPUT_FILE = "grayzone_articles.csv"
REQUEST_DELAY = 1  # seconds between page requests

# Extract and filter article links from HTML
def extract_articles(html, seen):
    soup = BeautifulSoup(html, "html.parser")
    articles = []
    for article in soup.find_all('article'):
        link_tag = article.find('a', href=True)
        if not link_tag:
            continue
        link = link_tag['href']
        if not TARGET_REGEX.match(link) or link in seen:
            continue

        title_tag = article.find(['h1', 'h2', 'h3', 'h4', 'h5', 'h6'])
        title = title_tag.get_text(strip=True) if title_tag else ""

        # Fetch the full article text
        try:
            article_resp = requests.get(link)
            article_resp.raise_for_status()
            article_soup = BeautifulSoup(article_resp.text, "html.parser")
            content_tags = article_soup.select(".entry-content p")
            content_text = " ".join(p.get_text(strip=True) for p in content_tags)
        except Exception as e:
            print(f"Error fetching article {link}: {e}")
            continue

        articles.append((link, title, content_text))
    return articles

# Main: iterate pages and collect unique articles
def main():
    seen_links = set()
    collected_articles = []
    page_numbers = [None] + list(range(2, MAX_PAGE + 1))

    for page in page_numbers:
        url = BASE_URL if page is None else PAGE_URL_TEMPLATE.format(page)
        try:
            print(f"Fetching page: {url}")
            resp = requests.get(url)
            resp.raise_for_status()
            articles = extract_articles(resp.text, seen_links)
            for link, title, content in articles:
                seen_links.add(link)
                collected_articles.append((link, title, content))
            print(f"  Found {len(articles)} new articles.")
            time.sleep(REQUEST_DELAY)
        except Exception as e:
            print(f"Error fetching {url}: {e}")
            continue

    # Write to CSV with index, title, text, label=1
    with open(OUTPUT_FILE, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(['index', 'title', 'text', 'label'])
        for idx, (link, title, content) in enumerate(collected_articles):
            writer.writerow([idx, title, content, 1])

    print(f"Collected {len(collected_articles)} unique articles. Saved to {OUTPUT_FILE}.")

if __name__ == '__main__':
    main()
