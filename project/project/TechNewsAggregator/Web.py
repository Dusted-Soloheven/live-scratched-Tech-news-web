"""
Web Class - Tech News Aggregator
A web scraping and aggregation class for gathering live tech news from the internet.
"""

import requests
from bs4 import BeautifulSoup
import time
import random
import re
import urllib.robotparser
from urllib.parse import urljoin, urlparse
from typing import List, Dict, Optional, Tuple
import json
from xml.etree import ElementTree as ET


class Web:
    """
    A class for web scraping and content aggregation.
    Implements responsible web scraping practices.
    """

    def __init__(self, user_agent: str = None):
        """
        Initialize the Web class with default settings.
        """
        self.user_agent = user_agent or "TechNewsAggregator/1.0 (Educational Project)"
        self.headers = {
            "User-Agent": self.user_agent,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
        }
        self.session = requests.Session()
        self.session.headers.update(self.headers)
        self.request_count = 0
        self.last_request_time = 0
        self.min_request_interval = 2.0
        self.robots_parsers = {}

    def _rate_limit(self):
        """
        Implement rate limiting to be respectful to servers.
        """
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        if time_since_last < self.min_request_interval:
            sleep_time = self.min_request_interval - time_since_last
            time.sleep(sleep_time)
        self.last_request_time = time.time()
        self.request_count += 1

    def fetch_page(self, url: str, timeout: int = 10) -> Optional[str]:
        """
        Fetch a web page with rate limiting and error handling.

        Args:
            url: The URL to fetch
            timeout: Request timeout in seconds

        Returns:
            HTML content or None if failed
        """
        if not self.check_robots_txt(url):
            print(f"Skipping {url}: blocked by robots.txt")
            return None

        try:
            self._rate_limit()
            response = self.session.get(url, timeout=timeout)
            response.raise_for_status()
            return response.text
        except requests.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    def parse_html(self, html: str) -> Optional[BeautifulSoup]:
        """
        Parse HTML content using BeautifulSoup.

        Args:
            html: Raw HTML string

        Returns:
            BeautifulSoup object or None if parsing fails
        """
        try:
            return BeautifulSoup(html, "html.parser")
        except Exception as e:
            print(f"Error parsing HTML: {e}")
            return None

    def extract_links(self, soup: BeautifulSoup, base_url: str = "") -> List[str]:
        """
        Extract all links from a parsed HTML page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of absolute URLs
        """
        links = []
        for link in soup.find_all("a", href=True):
            href = link["href"]
            absolute_url = urljoin(base_url, href)
            links.append(absolute_url)
        return links

    def extract_images(self, soup: BeautifulSoup, base_url: str = "") -> List[Dict[str, str]]:
        """
        Extract all images from a parsed HTML page.

        Args:
            soup: BeautifulSoup object
            base_url: Base URL for resolving relative links

        Returns:
            List of image dictionaries with src, alt, title
        """
        images = []
        for img in soup.find_all("img"):
            img_dict = {
                "src": urljoin(base_url, img.get("src", "")),
                "alt": img.get("alt", ""),
                "title": img.get("title", ""),
            }
            if img_dict["src"]:
                images.append(img_dict)
        return images

    def extract_text_content(self, soup: BeautifulSoup, selector: str = None) -> str:
        """
        Extract text content from HTML.

        Args:
            soup: BeautifulSoup object
            selector: Optional CSS selector for specific content

        Returns:
            Extracted text content
        """
        if selector:
            element = soup.select_one(selector)
            if element:
                return element.get_text(strip=True)
        return soup.get_text(separator=" ", strip=True)

    def fetch_news_from_rss(self, rss_url: str) -> List[Dict[str, str]]:
        """
        Fetch and parse news from RSS feed.

        Args:
            rss_url: URL of the RSS feed

        Returns:
            List of news items with title, link, description, pubDate
        """
        news_items = []
        html = self.fetch_page(rss_url)
        if not html:
            return news_items

        try:
            root = ET.fromstring(html)
        except ET.ParseError as e:
            print(f"Error parsing RSS feed {rss_url}: {e}")
            return news_items

        feed_type = self._get_local_tag(root.tag)

        if feed_type == "rss":
            for item in root.findall("./channel/item"):
                news_item = {
                    "title": self._clean_feed_text(self._get_child_text(item, "title")),
                    "link": self._clean_feed_text(self._get_child_text(item, "link")),
                    "description": self._clean_feed_text(self._get_child_text(item, "description")),
                    "pubDate": self._clean_feed_text(self._get_child_text(item, "pubDate")),
                }
                if news_item["title"]:
                    news_items.append(news_item)
        elif feed_type == "feed":
            for entry in root.findall("{http://www.w3.org/2005/Atom}entry"):
                link = self._get_atom_link(entry)
                news_item = {
                    "title": self._clean_feed_text(self._get_child_text(entry, "title")),
                    "link": self._clean_feed_text(link),
                    "description": self._clean_feed_text(
                        self._get_child_text(entry, "summary") or self._get_child_text(entry, "content")
                    ),
                    "pubDate": self._clean_feed_text(
                        self._get_child_text(entry, "published") or self._get_child_text(entry, "updated")
                    ),
                }
                if news_item["title"]:
                    news_items.append(news_item)

        return news_items

    def _get_local_tag(self, tag: str) -> str:
        if "}" in tag:
            return tag.split("}", 1)[1]
        return tag

    def _get_child_text(self, parent, tag_name: str) -> str:
        for child in parent:
            if self._get_local_tag(child.tag) == tag_name:
                return "".join(child.itertext()).strip()
        return ""

    def _get_atom_link(self, entry) -> str:
        for child in entry:
            if self._get_local_tag(child.tag) != "link":
                continue

            href = child.attrib.get("href", "").strip()
            rel = child.attrib.get("rel", "alternate").strip()
            if href and rel in ("alternate", ""):
                return href

        return ""

    def _clean_feed_text(self, text: str) -> str:
        if not text:
            return ""

        stripped = text.strip()
        if stripped.startswith(("http://", "https://")) and "<" not in stripped:
            return stripped

        # Feed descriptions often contain HTML fragments, so normalize them to plain text.
        return BeautifulSoup(stripped, "html.parser").get_text(" ", strip=True)

    def scrape_article_content(self, url: str, title_selector: str = "h1",
                               content_selector: str = "article, .content, main",
                               max_length: int = 2000) -> Optional[Dict[str, str]]:
        """
        Scrape article content from a news URL.

        Args:
            url: Article URL
            title_selector: CSS selector for title
            content_selector: CSS selector for main content
            max_length: Maximum content length

        Returns:
            Dictionary with title and content or None
        """
        html = self.fetch_page(url)
        if not html:
            return None

        soup = self.parse_html(html)
        if not soup:
            return None

        title_elem = soup.select_one(title_selector)
        content_elem = soup.select_one(content_selector)

        title = title_elem.get_text(strip=True) if title_elem else ""
        content = content_elem.get_text(separator=" ", strip=True)[:max_length] if content_elem else ""

        return {"title": title, "content": content, "url": url}

    def get_random_delay(self, min_sec: float = 1.0, max_sec: float = 3.0) -> float:
        """
        Get a random delay for respectful scraping.

        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds

        Returns:
            Random delay value
        """
        return random.uniform(min_sec, max_sec)

    def respectful_delay(self, min_sec: float = 2.0, max_sec: float = 5.0):
        """
        Sleep for a random period to avoid overwhelming servers.

        Args:
            min_sec: Minimum delay in seconds
            max_sec: Maximum delay in seconds
        """
        delay = self.get_random_delay(min_sec, max_sec)
        time.sleep(delay)

    def check_robots_txt(self, base_url: str) -> bool:
        """
        Check if a URL is allowed by robots.txt.

        Args:
            base_url: Base URL to check

        Returns:
            True if scraping is allowed, False otherwise
        """
        parsed = urlparse(base_url)
        if not parsed.scheme or not parsed.netloc:
            return True

        domain_key = f"{parsed.scheme}://{parsed.netloc}"
        robots_url = f"{domain_key}/robots.txt"

        parser = self.robots_parsers.get(domain_key)
        if parser is None:
            parser = urllib.robotparser.RobotFileParser()
            parser.set_url(robots_url)

            try:
                parser.read()
            except Exception:
                return True

            self.robots_parsers[domain_key] = parser

        try:
            return parser.can_fetch(self.user_agent, base_url)
        except Exception:
            return True

    def save_to_json(self, data: List[Dict], filename: str) -> bool:
        """
        Save scraped data to JSON file.

        Args:
            data: List of dictionaries to save
            filename: Output filename

        Returns:
            True if successful, False otherwise
        """
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"Error saving to JSON: {e}")
            return False

    def load_from_json(self, filename: str) -> Optional[List[Dict]]:
        """
        Load data from JSON file.

        Args:
            filename: Input filename

        Returns:
            List of dictionaries or None if failed
        """
        try:
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading from JSON: {e}")
            return None

    def get_request_count(self) -> int:
        """
        Get the number of requests made.

        Returns:
            Request count
        """
        return self.request_count

    def reset_request_count(self):
        """
        Reset the request counter.
        """
        self.request_count = 0


if __name__ == "__main__":
    web = Web()

    print("Web Class initialized successfully!")
    print(f"User Agent: {web.user_agent}")
