"""
Google News Scraper for Financial News Monitoring
Uses Google News RSS feeds directly
"""

import logging
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import re
import urllib.parse
from xml.etree import ElementTree as ET

try:
    import requests
except ImportError:
    requests = None

logger = logging.getLogger(__name__)


class NewsArticle:
    """Represents a news article with metadata"""

    def __init__(self, title: str, url: str, source: str,
                 published_date: Optional[datetime] = None,
                 description: str = ""):
        self.title = title
        self.url = url
        self.source = source
        self.published_date = published_date
        self.description = description

    def to_dict(self) -> Dict:
        """Convert article to dictionary"""
        return {
            'title': self.title,
            'url': self.url,
            'source': self.source,
            'published_date': self.published_date,
            'summary': self.description
        }


class GoogleNewsScraper:
    """Scraper for Google News using RSS feeds"""

    RSS_BASE_URL = "https://news.google.com/rss/search"

    def __init__(self, lookback_hours: int = 24, max_results: int = 10):
        """
        Initialize Google News scraper

        Args:
            lookback_hours: How many hours back to search for news
            max_results: Maximum number of results per search
        """
        if requests is None:
            raise ImportError("requests library not installed. Install with: pip install requests")

        self.lookback_hours = lookback_hours
        self.max_results = max_results

        logger.info(f"GoogleNewsScraper initialized (lookback: {lookback_hours}h, max: {max_results})")

    def search_news(self, query: str) -> List[NewsArticle]:
        """
        Search for news articles using a query

        Args:
            query: Search query string

        Returns:
            List of NewsArticle objects
        """
        try:
            logger.info(f"Searching for: {query}")

            # Build RSS URL with time constraint
            params = {
                'q': query,
                'hl': 'en-US',
                'gl': 'US',
                'ceid': 'US:en'
            }

            # Add time constraint (when:24h for last 24 hours)
            if self.lookback_hours <= 24:
                params['q'] = f"{query} when:{self.lookback_hours}h"

            url = f"{self.RSS_BASE_URL}?{urllib.parse.urlencode(params)}"

            # Fetch RSS feed
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }

            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Parse XML
            root = ET.fromstring(response.content)

            articles = []
            count = 0

            # Find all items in RSS feed
            for item in root.findall('.//item'):
                if count >= self.max_results:
                    break

                try:
                    title_elem = item.find('title')
                    link_elem = item.find('link')
                    pub_date_elem = item.find('pubDate')
                    description_elem = item.find('description')
                    source_elem = item.find('source')

                    title = title_elem.text if title_elem is not None else ""
                    url = link_elem.text if link_elem is not None else ""
                    description = description_elem.text if description_elem is not None else ""

                    # Parse source
                    source = "Unknown"
                    if source_elem is not None and source_elem.text:
                        source = source_elem.text

                    # Parse published date
                    published_date = None
                    if pub_date_elem is not None and pub_date_elem.text:
                        published_date = self._parse_date(pub_date_elem.text)

                    if title and url:
                        article = NewsArticle(
                            title=title,
                            url=url,
                            source=source,
                            published_date=published_date,
                            description=description
                        )
                        articles.append(article)
                        count += 1

                except Exception as e:
                    logger.warning(f"Error parsing article: {e}")
                    continue

            logger.info(f"Found {len(articles)} articles for query: {query}")
            return articles

        except requests.RequestException as e:
            logger.error(f"Error fetching news for '{query}': {e}")
            return []
        except ET.ParseError as e:
            logger.error(f"Error parsing RSS feed for '{query}': {e}")
            return []
        except Exception as e:
            logger.error(f"Unexpected error searching news for '{query}': {e}")
            return []

    def search_with_keywords(self, keywords: List[str], exclude: List[str] = None) -> List[NewsArticle]:
        """
        Search for news using multiple keywords (combined with OR)

        Args:
            keywords: List of keywords to search
            exclude: List of keywords to exclude

        Returns:
            List of NewsArticle objects
        """
        # Build query with OR operators
        query_parts = []

        # Add keywords with OR (limit to 5 for query length)
        if len(keywords) > 1:
            # Use quotes for multi-word keywords
            quoted_keywords = [f'"{kw}"' if ' ' in kw else kw for kw in keywords[:5]]
            query_parts.append(' OR '.join(quoted_keywords))
        elif len(keywords) == 1:
            query = f'"{keywords[0]}"' if ' ' in keywords[0] else keywords[0]
            query_parts.append(query)

        # Add exclusions
        if exclude:
            for exc in exclude:
                query_parts.append(f'-"{exc}"' if ' ' in exc else f'-{exc}')

        query = ' '.join(query_parts)
        return self.search_news(query)

    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """
        Try to parse date from various formats

        Args:
            date_str: Date string

        Returns:
            datetime object or None
        """
        # Common date formats (RSS usually uses RFC 822)
        formats = [
            '%a, %d %b %Y %H:%M:%S %Z',
            '%a, %d %b %Y %H:%M:%S %z',
            '%Y-%m-%d %H:%M:%S',
            '%Y-%m-%dT%H:%M:%SZ',
            '%Y-%m-%dT%H:%M:%S%z',
            '%Y-%m-%d',
        ]

        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except:
                continue

        # If all parsing fails, return None
        logger.warning(f"Could not parse date: {date_str}")
        return None

    def extract_deal_size(self, text: str) -> Optional[float]:
        """
        Extract deal size from text (in millions USD)

        Args:
            text: Text to search

        Returns:
            Deal size in millions or None
        """
        # Patterns for deal sizes
        patterns = [
            r'\$(\d+(?:\.\d+)?)\s*billion',
            r'\$(\d+(?:\.\d+)?)\s*bn',
            r'\$(\d+(?:\.\d+)?)\s*million',
            r'\$(\d+(?:\.\d+)?)\s*mn',
            r'(\d+(?:\.\d+)?)\s*billion',
            r'(\d+(?:\.\d+)?)\s*bn',
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                amount = float(match.group(1))

                # Convert to millions
                if 'billion' in pattern or 'bn' in pattern:
                    amount *= 1000

                return amount

        return None


class ArticlePrioritizer:
    """Determines priority level for articles"""

    def __init__(self, priority_funds: List[str],
                 deal_threshold: float = 500,
                 fund_close_threshold: float = 1000):
        """
        Initialize prioritizer

        Args:
            priority_funds: List of priority fund names
            deal_threshold: Minimum deal size for priority 2 (millions)
            fund_close_threshold: Minimum fund close for priority 2 (millions)
        """
        self.priority_funds = [f.lower() for f in priority_funds]
        self.deal_threshold = deal_threshold
        self.fund_close_threshold = fund_close_threshold

    def get_priority(self, article: NewsArticle, matched_keywords: List[str]) -> tuple:
        """
        Determine article priority

        Args:
            article: NewsArticle object
            matched_keywords: List of matched keywords

        Returns:
            Tuple of (priority_level, matched_priority_funds)
        """
        text = (article.title + ' ' + article.description).lower()

        # PRIORITY 1: Articles mentioning priority funds
        matched_funds = []
        for fund in self.priority_funds:
            if fund in text:
                matched_funds.append(fund)

        if matched_funds:
            return (1, matched_funds)

        # PRIORITY 2: Large deals or fund closes
        deal_size = self._extract_deal_size(text)

        # Check for deal announcements
        deal_keywords = ['acquisition', 'acquires', 'deal', 'transaction', 'investment']
        if deal_size and deal_size >= self.deal_threshold:
            if any(kw in text for kw in deal_keywords):
                return (2, [])

        # Check for fund closes
        fund_close_keywords = ['fund close', 'raises', 'raised', 'closes fund']
        if deal_size and deal_size >= self.fund_close_threshold:
            if any(kw in text for kw in fund_close_keywords):
                return (2, [])

        # PRIORITY 3: All other articles
        return (3, [])

    def _extract_deal_size(self, text: str) -> Optional[float]:
        """Extract deal size from text (in millions)"""
        patterns = [
            (r'\$(\d+(?:\.\d+)?)\s*billion', 1000),
            (r'\$(\d+(?:\.\d+)?)\s*bn', 1000),
            (r'(\d+(?:\.\d+)?)\s*billion', 1000),
            (r'(\d+(?:\.\d+)?)\s*bn', 1000),
            (r'\$(\d+(?:\.\d+)?)\s*million', 1),
            (r'\$(\d+(?:\.\d+)?)\s*mn', 1),
        ]

        for pattern, multiplier in patterns:
            match = re.search(pattern, text.lower())
            if match:
                return float(match.group(1)) * multiplier

        return None
