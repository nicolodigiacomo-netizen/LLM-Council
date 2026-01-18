"""
Configuration file for Financial News Monitoring System
"""

# Asset Classes and Keywords Configuration
ASSET_CLASSES = {
    "CLO_EQUITY": {
        "name": "CLO Equity",
        "keywords": [
            "CLO",
            "collateralized loan obligation",
            "CLO equity",
            "CLO manager",
            "CLO issuance",
            "CLO spreads",
            "leveraged loans",
            "Elmwood Asset Management",
            "CVC Credit Partners",
            "PGIM",
            "Sculptor Capital"
        ]
    },
    "SECONDARY_PRIVATE_EQUITY": {
        "name": "Secondary Private Equity",
        "keywords": [
            "secondary private equity",
            "secondaries market",
            "LP portfolio sale",
            "GP-led secondary",
            "continuation fund",
            "continuation vehicle",
            "tender offer",
            "single asset continuation",
            "GP-led transaction"
        ]
    },
    "PRIVATE_CREDIT": {
        "name": "Private Credit / Direct Lending",
        "keywords": [
            "direct lending",
            "private credit fund",
            "middle market lending",
            "BDC",
            "business development company",
            "unitranche",
            "private debt",
            "alternative credit",
            "direct lender"
        ]
    },
    "INFRASTRUCTURE": {
        "name": "Infrastructure",
        "keywords": [
            "infrastructure fund",
            "energy transition infrastructure",
            "digital infrastructure",
            "renewable energy fund",
            "infrastructure debt",
            "greenfield infrastructure",
            "brownfield infrastructure"
        ]
    },
    "CONTINUATION_FUNDS": {
        "name": "Continuation Funds",
        "keywords": [
            "continuation fund",
            "GP-led",
            "single asset continuation",
            "continuation vehicle",
            "portfolio continuation"
        ]
    }
}

# Priority Funds to Track
PRIORITY_FUNDS = [
    "Vista Equity Partners",
    "Axcel",
    "BC Partners",
    "Ion Pacific",
    "Astorg",
    "Hamilton Lane",
    "Lexington Partners",
    "Coller Capital"
]

# Deal size thresholds for priority classification (in millions USD)
PRIORITY_DEAL_THRESHOLD = 500
PRIORITY_FUND_CLOSE_THRESHOLD = 1000

# Priority keywords for deal announcements and fund closes
PRIORITY_KEYWORDS = [
    "acquisition",
    "acquires",
    "fund close",
    "raises",
    "raised",
    "closes fund",
    "billion",
    "million",
    "deal",
    "transaction",
    "investment"
]

# News search configuration
NEWS_LOOKBACK_HOURS = 24
MAX_ARTICLES_PER_ASSET_CLASS = 10

# Database configuration
DATABASE_PATH = "market_monitoring.db"

# Email configuration
EMAIL_SUBJECT = "Private Markets News Digest - {date}"
EMAIL_FROM_NAME = "Private Markets Monitor"

# Logging configuration
LOG_FILE = "monitoring.log"
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_LEVEL = "INFO"

# Output configuration
OUTPUT_DIR = "output"
DIGEST_FILENAME_TEMPLATE = "digest_{date}.html"
