#!/usr/bin/env python3
"""
fetch_worldnews.py

Fetch articles from World News API and save to CSV.

Usage:
    python fetch_worldnews.py \
        --api-key YOUR_API_KEY \
        --query "climate change" \
        --count 200 \
        --output articles.csv
"""

import os
import sys
import argparse
import requests
import csv
from time import sleep

API_URL = "https://api.worldnewsapi.com/search-news"

def fetch_articles(api_key: str,
                   query: str,
                   max_articles: int = 100,
                   page_size: int = 100,
                   **filters) -> list:
    """
    Fetch up to max_articles matching the given parameters.
    - api_key: your World News API key
    - query: full-text search string
    - max_articles: total number of articles to retrieve
    - page_size: number per request (<=100)
    - filters: other supported params (language, source_countries, earliest_publish_date, etc.)
    Returns list of article dicts.
    """
    articles = []
    offset = 0

    while len(articles) < max_articles:
        to_get = min(page_size, max_articles - len(articles))
        params = {
            'api-key': api_key,
            'text': query,
            'offset': offset,
            'number': to_get,
            **filters
        }
        resp = requests.get(API_URL, params=params)
        resp.raise_for_status()
        data = resp.json()

        batch = data.get('news', [])
        if not batch:
            break

        articles.extend(batch)
        offset += len(batch)

        # be gentle: sleep between requests
        sleep(0.2)

    return articles

def write_csv(path: str, articles: list):
    """
    Write articles to CSV with a predefined set of columns.
    """
    fieldnames = [
        'id', 'title', 'summary', 'url', 'publish_date',
        'authors', 'category', 'language', 'source_country',
        'sentiment', 'image', 'video'
    ]
    with open(path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for art in articles:
            row = {
                'id':                art.get('id'),
                'title':             art.get('title'),
                'summary':           art.get('summary'),
                'url':               art.get('url'),
                'publish_date':      art.get('publish_date'),
                'authors':           "|".join(art.get('authors', [])),
                'category':          art.get('category'),
                'language':          art.get('language'),
                'source_country':    art.get('source_country'),
                'sentiment':         art.get('sentiment'),
                'image':             art.get('image'),
                'video':             art.get('video'),
            }
            writer.writerow(row)

def main():
    parser = argparse.ArgumentParser(
        description="Fetch articles from World News API and save to CSV."
    )
    parser.add_argument('--api-key',  required=True,
                        help="Your World News API key")
    parser.add_argument('--query',    default="",
                        help="Full-text search query (at least one filter must be set)")
    parser.add_argument('--count',    type=int, default=100,
                        help="Total number of articles to fetch (max 100 per request)")
    parser.add_argument('--output',   default="articles.csv",
                        help="Path for the output CSV file")
    # You can add more filters here, e.g.:
    # parser.add_argument('--language', help="ISO-6391 language code")
    # parser.add_argument('--source-countries', help="Comma-separated ISO-3166 country codes")
    # parser.add_argument('--earliest-publish-date', help="YYYY-MM-DD")
    # parser.add_argument('--latest-publish-date', help="YYYY-MM-DD")
    args = parser.parse_args()

    print(f"Fetching up to {args.count} articles for query “{args.query}”…")
    articles = fetch_articles(
        api_key=args.api_key,
        query=args.query,
        max_articles=args.count,
        # e.g. language=args.language,
        # e.g. source_countries=args.source_countries,
        # earliest_publish_date=args.earliest_publish_date,
        # latest_publish_date=args.latest_publish_date,
    )
    print(f"Retrieved {len(articles)} articles; writing to {args.output}…")
    write_csv(args.output, articles)
    print("Done.")

if __name__ == '__main__':
    main()
