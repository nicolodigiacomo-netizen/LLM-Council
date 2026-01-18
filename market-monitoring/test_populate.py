#!/usr/bin/env python3
"""Populate database with sample articles for testing"""

import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.db_manager import DatabaseManager
import config

# Sample articles for testing
sample_articles = [
    {
        'title': 'Vista Equity Partners Closes $16.4 Billion Fund VIII',
        'source': 'Private Equity International',
        'url': 'https://www.privateequityinternational.com/vista-equity-fund-close-2026',
        'summary': 'Vista Equity Partners has closed its eighth flagship fund at $16.4 billion, marking one of the largest software-focused private equity funds raised this year. The fund exceeded its initial $14 billion target and will continue the firm\'s strategy of investing in enterprise software and technology-enabled businesses.',
        'asset_class': 'SECONDARY_PRIVATE_EQUITY',
        'priority': 1,
        'published_date': datetime.now() - timedelta(hours=2),
        'matched_keywords': ['continuation fund', 'private equity'],
        'matched_priority_funds': ['vista equity partners']
    },
    {
        'title': 'BC Partners Acquires European Healthcare Data Platform in €850M Deal',
        'source': 'Reuters',
        'url': 'https://www.reuters.com/bc-partners-healthcare-acquisition',
        'summary': 'BC Partners has agreed to acquire MedData Solutions, a leading European healthcare data analytics platform, in a transaction valued at approximately €850 million ($920 million). The deal represents BC Partners\' continued focus on digital transformation in the healthcare sector.',
        'asset_class': 'PRIVATE_CREDIT',
        'priority': 1,
        'published_date': datetime.now() - timedelta(hours=5),
        'matched_keywords': ['acquisition', 'private equity'],
        'matched_priority_funds': ['bc partners']
    },
    {
        'title': 'Hamilton Lane Reports Record Secondaries Activity in Q4 2025',
        'source': 'Financial Times',
        'url': 'https://www.ft.com/hamilton-lane-secondaries-q4',
        'summary': 'Hamilton Lane reported record secondary transaction volume in Q4 2025, completing $4.2 billion in LP portfolio sales and GP-led transactions. The firm notes strong demand for continuation funds as GPs seek to extend hold periods for their best-performing assets.',
        'asset_class': 'SECONDARY_PRIVATE_EQUITY',
        'priority': 1,
        'published_date': datetime.now() - timedelta(hours=8),
        'matched_keywords': ['secondaries market', 'continuation fund', 'GP-led'],
        'matched_priority_funds': ['hamilton lane']
    },
    {
        'title': 'Infrastructure Fund Closes at $7.5 Billion for Renewable Energy Projects',
        'source': 'Bloomberg',
        'url': 'https://www.bloomberg.com/infrastructure-fund-renewable-energy',
        'summary': 'Global Infrastructure Partners has closed its fifth infrastructure fund at $7.5 billion, significantly exceeding its $6 billion target. The fund will focus on renewable energy and energy transition projects across North America and Europe, with particular emphasis on solar, wind, and battery storage infrastructure.',
        'asset_class': 'INFRASTRUCTURE',
        'priority': 2,
        'published_date': datetime.now() - timedelta(hours=12),
        'matched_keywords': ['infrastructure fund', 'renewable energy fund', 'fund close'],
        'matched_priority_funds': []
    },
    {
        'title': 'CLO Issuance Surges 45% Year-Over-Year as Spreads Tighten',
        'source': 'S&P Global',
        'url': 'https://www.spglobal.com/clo-issuance-surge-2026',
        'summary': 'Collateralized loan obligation issuance has surged 45% compared to the same period last year, with $28.5 billion in new CLOs priced in January alone. Market participants cite tightening spreads and strong investor appetite for AAA-rated tranches as key drivers. CLO equity returns have averaged 15.2% over the past 12 months.',
        'asset_class': 'CLO_EQUITY',
        'priority': 3,
        'published_date': datetime.now() - timedelta(hours=15),
        'matched_keywords': ['CLO', 'CLO issuance', 'CLO equity', 'CLO spreads'],
        'matched_priority_funds': []
    },
    {
        'title': 'Ares Management Launches $2.1B Direct Lending Fund for Middle Market',
        'source': 'Wall Street Journal',
        'url': 'https://www.wsj.com/ares-direct-lending-fund',
        'summary': 'Ares Management Corporation announced the close of its latest direct lending fund at $2.1 billion, targeting unitranche financing for North American middle market companies. The fund will provide flexible capital solutions with ticket sizes ranging from $50 million to $500 million.',
        'asset_class': 'PRIVATE_CREDIT',
        'priority': 2,
        'published_date': datetime.now() - timedelta(hours=18),
        'matched_keywords': ['direct lending', 'private credit fund', 'middle market lending', 'unitranche'],
        'matched_priority_funds': []
    },
    {
        'title': 'Lexington Partners Completes $3.2B GP-Led Secondary Transaction',
        'source': 'PEI News',
        'url': 'https://www.penews.com/lexington-gp-led-transaction',
        'summary': 'Lexington Partners has completed a $3.2 billion GP-led secondary transaction involving a portfolio of software and technology assets. The continuation vehicle structure allows the original GP to maintain ownership while providing liquidity to existing LPs. This marks Lexington\'s largest single GP-led transaction to date.',
        'asset_class': 'SECONDARY_PRIVATE_EQUITY',
        'priority': 1,
        'published_date': datetime.now() - timedelta(hours=20),
        'matched_keywords': ['GP-led', 'continuation vehicle', 'secondary private equity'],
        'matched_priority_funds': ['lexington partners']
    },
    {
        'title': 'BDCs Report Strong Performance Amid Rising Private Credit Allocations',
        'source': 'Institutional Investor',
        'url': 'https://www.institutionalinvestor.com/bdc-performance-2026',
        'summary': 'Business development companies reported average NAV returns of 11.8% in Q4 2025, benefiting from higher base rates and strong credit quality. Institutional allocations to private credit strategies continue to grow, with pension funds and insurers increasing exposure to the asset class.',
        'asset_class': 'PRIVATE_CREDIT',
        'priority': 3,
        'published_date': datetime.now() - timedelta(hours=22),
        'matched_keywords': ['BDC', 'business development company', 'private credit', 'direct lender'],
        'matched_priority_funds': []
    },
    {
        'title': 'Digital Infrastructure Investment Reaches $42B in 2025',
        'source': 'Infrastructure Investor',
        'url': 'https://www.infrastructureinvestor.com/digital-infrastructure-2025',
        'summary': 'Investment in digital infrastructure assets, including data centers, fiber networks, and cell towers, reached $42 billion globally in 2025, up 28% from the prior year. The growth is driven by AI computational demands and 5G network buildouts across major markets.',
        'asset_class': 'INFRASTRUCTURE',
        'priority': 3,
        'published_date': datetime.now() - timedelta(hours=24),
        'matched_keywords': ['digital infrastructure', 'infrastructure fund'],
        'matched_priority_funds': []
    },
    {
        'title': 'Coller Capital Announces $8.5B Close for Ninth International Fund',
        'source': 'Alternative Assets',
        'url': 'https://www.alternativeassets.com/coller-fund-close',
        'summary': 'Coller Capital, a pioneer in the secondary private equity market, has announced the final close of its ninth international secondaries fund at $8.5 billion. The fund attracted strong interest from institutional investors globally and will focus on LP portfolio acquisitions and GP-led restructurings across all private equity strategies.',
        'asset_class': 'SECONDARY_PRIVATE_EQUITY',
        'priority': 1,
        'published_date': datetime.now() - timedelta(hours=3),
        'matched_keywords': ['secondary private equity', 'secondaries market', 'fund close'],
        'matched_priority_funds': ['coller capital']
    }
]

def main():
    print("Populating database with sample articles...")

    db = DatabaseManager(config.DATABASE_PATH)

    inserted = 0
    for article in sample_articles:
        if db.insert_article(article):
            inserted += 1
            print(f"  ✓ {article['title'][:60]}...")

    print(f"\n✅ Inserted {inserted} sample articles")

    # Show stats
    stats = db.get_statistics()
    print(f"\n📊 Database Statistics:")
    print(f"  Total articles: {stats['total_articles']}")
    print(f"  Priority 1: {stats['by_priority'].get(1, 0)}")
    print(f"  Priority 2: {stats['by_priority'].get(2, 0)}")
    print(f"  Priority 3: {stats['by_priority'].get(3, 0)}")

if __name__ == "__main__":
    main()
