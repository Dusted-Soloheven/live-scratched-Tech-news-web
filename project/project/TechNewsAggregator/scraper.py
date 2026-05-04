"""
Scraper - Fetch Real Tech News Data
This script uses the Web class to gather live tech news from multiple sources.
"""

import json
import time
from Web import Web
import random

def get_random_tech_comment(news_title: str) -> str:
    """Generate a relevant comment based on news content."""
    comments = [
        f"Intriguing development in the tech world: {news_title[:50]}...",
        f"This news about {news_title[:40]} reflects the rapid pace of tech innovation.",
        f"Interesting news: {news_title[:45]} - the tech landscape continues to evolve.",
        f"News about {news_title[:35]} highlights the dynamic nature of the industry.",
        f"Story on {news_title[:40]} shows how technology continues to transform our lives.",
    ]
    return random.choice(comments)

def main():
    print("=" * 60)
    print("Tech News Aggregator - Web Scraper")
    print("=" * 60)

    web = Web()
    all_news = []

    sources = [
        {
            "name": "TechCrunch",
            "rss_url": "https://techcrunch.com/feed/",
            "category": "tech"
        },
        {
            "name": "The Verge",
            "rss_url": "https://www.theverge.com/rss/index.xml",
            "category": "tech"
        },
        {
            "name": "Engadget",
            "rss_url": "https://www.engadget.com/rss.xml",
            "category": "tech"
        }
    ]

    print("\nFetching news from multiple sources...")
    print("Respectful scraping with robots.txt checks, rate limiting, and delays enabled.\n")

    for source in sources:
        print(f"  [*] Fetching from {source['name']}...")
        try:
            news_items = web.fetch_news_from_rss(source['rss_url'])

            for item in news_items[:5]:
                news_entry = {
                    "source": source['name'],
                    "title": item.get('title', ''),
                    "link": item.get('link', ''),
                    "description": item.get('description', '')[:200] + '...' if len(item.get('description', '')) > 200 else item.get('description', ''),
                    "pubDate": item.get('pubDate', ''),
                    "category": source['category'],
                    "ai_comment": get_random_tech_comment(item.get('title', ''))
                }
                all_news.append(news_entry)

            print(f"      + Retrieved {len(news_items[:5])} articles from {source['name']}")

            web.respectful_delay(2, 4)

        except Exception as e:
            print(f"      - Error fetching from {source['name']}: {e}")
            continue

    print(f"\n{'=' * 60}")
    print(f"Total articles collected: {len(all_news)}")
    print(f"Total requests made: {web.get_request_count()}")
    print("=" * 60)

    output_file = "scraped_news.json"
    if web.save_to_json(all_news, output_file):
        print(f"\n+ News data saved to: {output_file}")
    else:
        print(f"\n- Failed to save data")

    print("\n" + "=" * 60)
    print("Sample of scraped news:")
    print("=" * 60)

    for i, news in enumerate(all_news[:3], 1):
        print(f"\n{i}. [{news['source']}]")
        print(f"   Title: {news['title']}")
        print(f"   AI Comment: {news['ai_comment']}")
        print(f"   Link: {news['link']}")

    return all_news

if __name__ == "__main__":
    news_data = main()
