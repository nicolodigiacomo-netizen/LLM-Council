#!/usr/bin/env python3
"""Generate email digest from database articles"""

import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
from emailer.digest import DigestGenerator
import config

def main():
    print("Generating email digest...")

    # Get articles from database
    db = DatabaseManager(config.DATABASE_PATH)
    articles = db.get_recent_articles(hours=24)

    print(f"Found {len(articles)} articles")

    # Generate HTML
    generator = DigestGenerator(config.ASSET_CLASSES)
    date_str = datetime.now().strftime('%B %d, %Y')
    html = generator.generate_html(articles, date_str)

    # Save to output
    os.makedirs(config.OUTPUT_DIR, exist_ok=True)
    output_filename = f"digest_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
    output_path = os.path.join(config.OUTPUT_DIR, output_filename)

    generator.save_digest(html, output_path)

    print(f"✅ Digest saved to: {output_path}")
    print(f"\nPreview the digest:")
    print(f"  File: {output_path}")
    print(f"\nArticles by priority:")
    priority_1 = [a for a in articles if a['priority'] == 1]
    priority_2 = [a for a in articles if a['priority'] == 2]
    priority_3 = [a for a in articles if a['priority'] == 3]

    print(f"  🔴 Priority 1 (Key Funds): {len(priority_1)} articles")
    for a in priority_1:
        print(f"     - {a['title'][:70]}...")

    print(f"\n  🟡 Priority 2 (Major Deals): {len(priority_2)} articles")
    for a in priority_2:
        print(f"     - {a['title'][:70]}...")

    print(f"\n  📊 Priority 3 (Market Trends): {len(priority_3)} articles")
    for a in priority_3:
        print(f"     - {a['title'][:70]}...")

if __name__ == "__main__":
    main()
