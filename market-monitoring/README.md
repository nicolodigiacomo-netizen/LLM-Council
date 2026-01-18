# Financial News Monitoring System for Private Markets

An automated system for monitoring and aggregating financial news across private markets asset classes, including CLO Equity, Secondary Private Equity, Private Credit, Infrastructure, and Continuation Funds.

## Features

- **Automated News Scraping**: Uses Google News to find relevant articles for each asset class
- **Smart Prioritization**:
  - Priority 1: Articles mentioning key funds (Vista Equity, Axcel, BC Partners, etc.)
  - Priority 2: Major deals ($500M+) and fund closes ($1B+)
  - Priority 3: Industry trends and market analysis
- **SQLite Database**: Tracks all articles and prevents duplicates
- **HTML Email Digest**: Professional, mobile-friendly daily digest
- **Offline Storage**: Saves HTML digests in `/output` folder for offline review

## Asset Classes Monitored

1. **CLO Equity**: Collateralized Loan Obligations and leveraged loans
2. **Secondary Private Equity**: LP portfolio sales, GP-led secondaries, continuation funds
3. **Private Credit / Direct Lending**: Middle market lending, BDCs, alternative credit
4. **Infrastructure**: Energy transition, digital infrastructure, renewable energy
5. **Continuation Funds**: GP-led transactions and single asset continuations

## Priority Funds Tracked

- Vista Equity Partners
- Axcel
- BC Partners
- Ion Pacific
- Astorg
- Hamilton Lane
- Lexington Partners
- Coller Capital

## Project Structure

```
market-monitoring/
├── monitor.py              # Main script
├── config.py               # Configuration and settings
├── requirements.txt        # Python dependencies
├── .env.example           # Environment variables template
├── .gitignore             # Git ignore rules
├── README.md              # This file
├── scrapers/
│   ├── __init__.py
│   └── google_news.py     # Google News scraper
├── database/
│   ├── __init__.py
│   └── db_manager.py      # SQLite database manager
├── emailer/
│   ├── __init__.py
│   └── digest.py          # Email digest generator
└── output/                # Saved HTML digests
```

## Installation

### Prerequisites

- Python 3.8 or higher
- pip (Python package manager)
- Gmail account with App Password (for email sending)

### Step-by-Step Setup

#### 1. Clone or Download the Project

```bash
cd market-monitoring
```

#### 2. Create Virtual Environment (Recommended)

**On macOS/Linux:**
```bash
python3 -m venv venv
source venv/bin/activate
```

**On Windows:**
```bash
python -m venv venv
venv\Scripts\activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Configure Environment Variables

Copy the example file:
```bash
cp .env.example .env
```

Edit `.env` with your email credentials:
```bash
# For macOS/Linux
nano .env

# For Windows
notepad .env
```

Fill in your details:
```
EMAIL_TO=nicolo.digiacomo@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
```

#### 5. Set Up Gmail App Password

For Gmail, you **must** use an App Password (not your regular password):

1. Enable 2-Factor Authentication on your Google account:
   - Go to https://myaccount.google.com/security
   - Enable "2-Step Verification"

2. Generate an App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and your device
   - Copy the 16-character password
   - Use this in your `.env` file as `SMTP_PASSWORD`

## Usage

### Run Manual Test

To test the system and generate a digest:

```bash
python monitor.py
```

This will:
1. Search for news from the last 24 hours
2. Save articles to SQLite database
3. Generate HTML digest in `/output` folder
4. Send email digest (if configured)
5. Display statistics and logs

### Test Without Sending Email

To test without sending email, set in `.env`:
```
SKIP_EMAIL_SEND=true
```

### Schedule Automatic Runs

#### On macOS/Linux (cron)

Edit crontab:
```bash
crontab -e
```

Add line to run daily at 8 AM:
```
0 8 * * * cd /path/to/market-monitoring && /path/to/venv/bin/python monitor.py >> monitoring.log 2>&1
```

#### On Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger to Daily at 8:00 AM
4. Set action to:
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `monitor.py`
   - Start in: `C:\path\to\market-monitoring`

## Configuration

### Modify Asset Classes and Keywords

Edit `config.py` to add/remove asset classes or keywords:

```python
ASSET_CLASSES = {
    "YOUR_ASSET_CLASS": {
        "name": "Display Name",
        "keywords": [
            "keyword1",
            "keyword2",
            # ... more keywords
        ]
    }
}
```

### Modify Priority Funds

Edit `config.py`:

```python
PRIORITY_FUNDS = [
    "Fund Name 1",
    "Fund Name 2",
    # ... more funds
]
```

### Adjust Search Parameters

In `config.py`:

```python
NEWS_LOOKBACK_HOURS = 24  # How many hours back to search
MAX_ARTICLES_PER_ASSET_CLASS = 10  # Max articles per search
PRIORITY_DEAL_THRESHOLD = 500  # Minimum deal size (millions)
PRIORITY_FUND_CLOSE_THRESHOLD = 1000  # Minimum fund close (millions)
```

## Database

The system uses SQLite database (`market_monitoring.db`) to store articles.

### View Database

Using SQLite command line:
```bash
sqlite3 market_monitoring.db
.tables
SELECT * FROM articles LIMIT 10;
```

Using Python:
```python
import sqlite3
conn = sqlite3.connect('market_monitoring.db')
cursor = conn.cursor()
cursor.execute('SELECT title, source, priority FROM articles ORDER BY scraped_date DESC LIMIT 10')
for row in cursor.fetchall():
    print(row)
```

## Troubleshooting

### gnews Library Not Found

```bash
pip install gnews
```

### SMTP Authentication Error

- Make sure you're using an App Password, not your regular Gmail password
- Verify 2-Factor Authentication is enabled on your Google account
- Check that `SMTP_USER` is your full Gmail address

### No Articles Found

- Google News API has rate limits - wait a few hours and try again
- Some keywords may not return results - check if they're too specific
- Try testing with a single popular keyword first

### Network/Proxy Errors (403 Forbidden)

If you see "403 Forbidden" or proxy errors:
- This typically occurs in corporate networks or restricted environments
- Check if your network has a firewall or proxy blocking news.google.com
- Try running from a different network (home WiFi, personal hotspot)
- In corporate environments, you may need to configure proxy settings or whitelist Google News

### Database Locked Error

- Make sure only one instance of `monitor.py` is running
- If error persists, delete `market_monitoring.db` to start fresh

### ImportError or ModuleNotFoundError

Make sure you've activated the virtual environment:
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate
```

Then reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Output Files

- **monitoring.log**: Detailed logs of all operations
- **market_monitoring.db**: SQLite database with all articles
- **output/digest_YYYYMMDD_HHMMSS.html**: Saved HTML digests

## Security Notes

- Never commit `.env` file to git (it's in `.gitignore`)
- Keep your App Password secure
- Regularly rotate your App Passwords
- Use a dedicated email account for automated systems

## Customization

### Change Email Template

Edit `emailer/digest.py` to modify the HTML template styling and structure.

### Add New Scrapers

Create new scraper in `scrapers/` folder following the pattern in `google_news.py`.

### Modify Priority Logic

Edit the `ArticlePrioritizer` class in `scrapers/google_news.py`.

## Support

For issues or questions:
1. Check the logs in `monitoring.log`
2. Review troubleshooting section above
3. Verify all dependencies are installed correctly

## License

This project is for internal use. Modify and distribute as needed for your organization.

---

**Last Updated**: January 2026
**Version**: 1.0.0
