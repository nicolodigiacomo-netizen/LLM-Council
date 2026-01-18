"""
Database Manager for Financial News Monitoring System
Handles all SQLite database operations
"""

import sqlite3
import logging
from datetime import datetime
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Manages SQLite database operations for news articles"""

    def __init__(self, db_path: str):
        """
        Initialize database manager

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Create database tables if they don't exist"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                CREATE TABLE IF NOT EXISTS articles (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    title TEXT NOT NULL,
                    source TEXT NOT NULL,
                    url TEXT UNIQUE NOT NULL,
                    summary TEXT,
                    asset_class TEXT NOT NULL,
                    priority INTEGER NOT NULL,
                    published_date TIMESTAMP,
                    scraped_date TIMESTAMP NOT NULL,
                    matched_keywords TEXT,
                    matched_priority_funds TEXT
                )
            ''')

            # Create index on URL for faster duplicate checking
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_url ON articles(url)
            ''')

            # Create index on published_date for faster date range queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_published_date ON articles(published_date)
            ''')

            conn.commit()
            conn.close()
            logger.info("Database initialized successfully")

        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise

    def article_exists(self, url: str) -> bool:
        """
        Check if article already exists in database

        Args:
            url: Article URL

        Returns:
            True if article exists, False otherwise
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('SELECT COUNT(*) FROM articles WHERE url = ?', (url,))
            count = cursor.fetchone()[0]

            conn.close()
            return count > 0

        except Exception as e:
            logger.error(f"Error checking article existence: {e}")
            return False

    def insert_article(self, article: Dict) -> bool:
        """
        Insert new article into database

        Args:
            article: Dictionary containing article data

        Returns:
            True if successful, False otherwise
        """
        try:
            # Check if article already exists
            if self.article_exists(article['url']):
                logger.debug(f"Article already exists: {article['url']}")
                return False

            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO articles
                (title, source, url, summary, asset_class, priority,
                 published_date, scraped_date, matched_keywords, matched_priority_funds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                article.get('title', ''),
                article.get('source', ''),
                article['url'],
                article.get('summary', ''),
                article.get('asset_class', ''),
                article.get('priority', 3),
                article.get('published_date'),
                datetime.now(),
                ','.join(article.get('matched_keywords', [])),
                ','.join(article.get('matched_priority_funds', []))
            ))

            conn.commit()
            conn.close()
            logger.info(f"Article inserted: {article['title']}")
            return True

        except Exception as e:
            logger.error(f"Error inserting article: {e}")
            return False

    def get_recent_articles(self, hours: int = 24) -> List[Dict]:
        """
        Get articles from the last N hours

        Args:
            hours: Number of hours to look back

        Returns:
            List of article dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM articles
                WHERE scraped_date >= datetime('now', '-' || ? || ' hours')
                ORDER BY priority ASC, published_date DESC
            ''', (hours,))

            rows = cursor.fetchall()
            articles = [dict(row) for row in rows]

            # Parse matched keywords and funds back into lists
            for article in articles:
                if article['matched_keywords']:
                    article['matched_keywords'] = article['matched_keywords'].split(',')
                else:
                    article['matched_keywords'] = []

                if article['matched_priority_funds']:
                    article['matched_priority_funds'] = article['matched_priority_funds'].split(',')
                else:
                    article['matched_priority_funds'] = []

            conn.close()
            logger.info(f"Retrieved {len(articles)} articles from last {hours} hours")
            return articles

        except Exception as e:
            logger.error(f"Error retrieving recent articles: {e}")
            return []

    def get_articles_by_priority(self, priority: int, hours: int = 24) -> List[Dict]:
        """
        Get articles of a specific priority level

        Args:
            priority: Priority level (1, 2, or 3)
            hours: Number of hours to look back

        Returns:
            List of article dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM articles
                WHERE priority = ?
                AND scraped_date >= datetime('now', '-' || ? || ' hours')
                ORDER BY published_date DESC
            ''', (priority, hours))

            rows = cursor.fetchall()
            articles = [dict(row) for row in rows]

            # Parse matched keywords and funds back into lists
            for article in articles:
                if article['matched_keywords']:
                    article['matched_keywords'] = article['matched_keywords'].split(',')
                else:
                    article['matched_keywords'] = []

                if article['matched_priority_funds']:
                    article['matched_priority_funds'] = article['matched_priority_funds'].split(',')
                else:
                    article['matched_priority_funds'] = []

            conn.close()
            return articles

        except Exception as e:
            logger.error(f"Error retrieving articles by priority: {e}")
            return []

    def get_articles_by_asset_class(self, asset_class: str, hours: int = 24) -> List[Dict]:
        """
        Get articles for a specific asset class

        Args:
            asset_class: Asset class identifier
            hours: Number of hours to look back

        Returns:
            List of article dictionaries
        """
        try:
            conn = sqlite3.connect(self.db_path)
            conn.row_factory = sqlite3.Row
            cursor = conn.cursor()

            cursor.execute('''
                SELECT * FROM articles
                WHERE asset_class = ?
                AND scraped_date >= datetime('now', '-' || ? || ' hours')
                ORDER BY priority ASC, published_date DESC
            ''', (asset_class, hours))

            rows = cursor.fetchall()
            articles = [dict(row) for row in rows]

            # Parse matched keywords and funds back into lists
            for article in articles:
                if article['matched_keywords']:
                    article['matched_keywords'] = article['matched_keywords'].split(',')
                else:
                    article['matched_keywords'] = []

                if article['matched_priority_funds']:
                    article['matched_priority_funds'] = article['matched_priority_funds'].split(',')
                else:
                    article['matched_priority_funds'] = []

            conn.close()
            return articles

        except Exception as e:
            logger.error(f"Error retrieving articles by asset class: {e}")
            return []

    def get_statistics(self) -> Dict:
        """
        Get database statistics

        Returns:
            Dictionary with statistics
        """
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()

            stats = {}

            # Total articles
            cursor.execute('SELECT COUNT(*) FROM articles')
            stats['total_articles'] = cursor.fetchone()[0]

            # Articles in last 24 hours
            cursor.execute('''
                SELECT COUNT(*) FROM articles
                WHERE scraped_date >= datetime('now', '-24 hours')
            ''')
            stats['articles_last_24h'] = cursor.fetchone()[0]

            # Articles by priority
            cursor.execute('''
                SELECT priority, COUNT(*) as count
                FROM articles
                WHERE scraped_date >= datetime('now', '-24 hours')
                GROUP BY priority
            ''')
            stats['by_priority'] = dict(cursor.fetchall())

            # Articles by asset class
            cursor.execute('''
                SELECT asset_class, COUNT(*) as count
                FROM articles
                WHERE scraped_date >= datetime('now', '-24 hours')
                GROUP BY asset_class
            ''')
            stats['by_asset_class'] = dict(cursor.fetchall())

            conn.close()
            return stats

        except Exception as e:
            logger.error(f"Error retrieving statistics: {e}")
            return {}
