#!/usr/bin/env python3
"""
Financial News Monitoring System for Private Markets
Main script to scrape, analyze, and send news digest
"""

import os
import sys
import logging
from datetime import datetime
from typing import List, Dict
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

# Import project modules
import config
from database.db_manager import DatabaseManager
from scrapers.google_news import GoogleNewsScraper, ArticlePrioritizer
from emailer.digest import DigestGenerator, EmailSender


def setup_logging():
    """Configure logging for the application"""
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )


def scrape_news_for_asset_class(scraper: GoogleNewsScraper, prioritizer: ArticlePrioritizer,
                                  asset_class_key: str, asset_class_config: Dict,
                                  db_manager: DatabaseManager) -> int:
    """
    Scrape news for a single asset class

    Args:
        scraper: GoogleNewsScraper instance
        prioritizer: ArticlePrioritizer instance
        asset_class_key: Asset class identifier
        asset_class_config: Asset class configuration dict
        db_manager: DatabaseManager instance

    Returns:
        Number of new articles found
    """
    logger = logging.getLogger(__name__)
    logger.info(f"Scraping news for: {asset_class_config['name']}")

    keywords = asset_class_config['keywords']
    articles = scraper.search_with_keywords(keywords)

    new_articles = 0

    for article in articles:
        # Determine priority
        matched_keywords = []
        article_text = (article.title + ' ' + article.description).lower()

        for keyword in keywords:
            if keyword.lower() in article_text:
                matched_keywords.append(keyword)

        priority, matched_funds = prioritizer.get_priority(article, matched_keywords)

        # Prepare article data
        article_data = article.to_dict()
        article_data['asset_class'] = asset_class_key
        article_data['priority'] = priority
        article_data['matched_keywords'] = matched_keywords[:10]  # Limit to 10
        article_data['matched_priority_funds'] = matched_funds

        # Insert into database
        if db_manager.insert_article(article_data):
            new_articles += 1

    logger.info(f"Found {new_articles} new articles for {asset_class_config['name']}")
    return new_articles


def main():
    """Main execution function"""
    logger = logging.getLogger(__name__)

    print("=" * 60)
    print("Financial News Monitoring System - Private Markets")
    print("=" * 60)
    print()

    # Initialize components
    logger.info("Initializing monitoring system...")

    # Database
    db_manager = DatabaseManager(config.DATABASE_PATH)

    # Scraper
    try:
        scraper = GoogleNewsScraper(
            lookback_hours=config.NEWS_LOOKBACK_HOURS,
            max_results=config.MAX_ARTICLES_PER_ASSET_CLASS
        )
    except ImportError as e:
        logger.error(f"Failed to initialize scraper: {e}")
        print("\n❌ Error: gnews library not installed.")
        print("Please install it with: pip install gnews")
        return 1

    # Prioritizer
    prioritizer = ArticlePrioritizer(
        priority_funds=config.PRIORITY_FUNDS,
        deal_threshold=config.PRIORITY_DEAL_THRESHOLD,
        fund_close_threshold=config.PRIORITY_FUND_CLOSE_THRESHOLD
    )

    # Scrape news for each asset class
    print(f"🔍 Searching for news from the last {config.NEWS_LOOKBACK_HOURS} hours...\n")

    total_new_articles = 0

    for asset_class_key, asset_class_config in config.ASSET_CLASSES.items():
        new_count = scrape_news_for_asset_class(
            scraper, prioritizer, asset_class_key, asset_class_config, db_manager
        )
        total_new_articles += new_count

        print(f"  ✓ {asset_class_config['name']}: {new_count} new articles")

    print(f"\n📊 Total new articles found: {total_new_articles}")

    # Get statistics
    stats = db_manager.get_statistics()
    print(f"📈 Database statistics:")
    print(f"  - Total articles in database: {stats.get('total_articles', 0)}")
    print(f"  - Articles in last 24h: {stats.get('articles_last_24h', 0)}")

    if stats.get('by_priority'):
        print(f"  - By priority: {stats['by_priority']}")

    # Generate digest
    print(f"\n📧 Generating email digest...")

    articles = db_manager.get_recent_articles(hours=config.NEWS_LOOKBACK_HOURS)

    if not articles:
        print("  ℹ️  No articles to include in digest")
        logger.info("No articles found for digest")
        return 0

    # Generate HTML
    digest_generator = DigestGenerator(config.ASSET_CLASSES)
    date_str = datetime.now().strftime('%B %d, %Y')
    html_content = digest_generator.generate_html(articles, date_str)

    # Save digest to output directory
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    output_filename = config.DIGEST_FILENAME_TEMPLATE.format(
        date=datetime.now().strftime('%Y%m%d_%H%M%S')
    )
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)

    if digest_generator.save_digest(html_content, output_path):
        print(f"  ✓ Digest saved to: {output_path}")

    # Send email
    email_to = os.getenv('EMAIL_TO')
    smtp_server = os.getenv('SMTP_SERVER')
    smtp_port = int(os.getenv('SMTP_PORT', 587))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    skip_email = os.getenv('SKIP_EMAIL_SEND', 'false').lower() == 'true'

    if skip_email:
        print("  ⚠️  Email sending skipped (SKIP_EMAIL_SEND=true)")
        logger.info("Email sending skipped by configuration")
    elif not all([email_to, smtp_server, smtp_user, smtp_password]):
        print("  ⚠️  Email not configured. Please set up .env file")
        print("  ℹ️  Copy .env.example to .env and fill in your credentials")
        logger.warning("Email credentials not configured")
    else:
        try:
            email_sender = EmailSender(
                smtp_server=smtp_server,
                smtp_port=smtp_port,
                smtp_user=smtp_user,
                smtp_password=smtp_password,
                from_name=config.EMAIL_FROM_NAME
            )

            subject = config.EMAIL_SUBJECT.format(date=date_str)

            if email_sender.send_digest(email_to, subject, html_content):
                print(f"  ✓ Email sent successfully to: {email_to}")
            else:
                print(f"  ❌ Failed to send email (check logs for details)")

        except Exception as e:
            logger.error(f"Error sending email: {e}")
            print(f"  ❌ Error sending email: {e}")

    print(f"\n✅ Monitoring completed successfully!")
    print("=" * 60)

    return 0


if __name__ == "__main__":
    setup_logging()
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interrupted by user")
        sys.exit(1)
    except Exception as e:
        logging.error(f"Unexpected error: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        sys.exit(1)
