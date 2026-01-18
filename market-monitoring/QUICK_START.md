# Quick Start Guide

## 5-Minute Setup

### 1. Install Dependencies (1 min)

```bash
cd market-monitoring
pip install -r requirements.txt
```

### 2. Configure Email (2 min)

```bash
# Copy template
cp .env.example .env

# Edit .env file
nano .env  # or use any text editor
```

Fill in your Gmail credentials:
```
EMAIL_TO=nicolo.digiacomo@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password  # Get from https://myaccount.google.com/apppasswords
```

**Important**: Use a Gmail App Password, not your regular password!

### 3. Run First Test (2 min)

```bash
# Test without sending email
echo "SKIP_EMAIL_SEND=true" >> .env
python monitor.py
```

You should see:
```
============================================================
Financial News Monitoring System - Private Markets
============================================================

🔍 Searching for news from the last 24 hours...

  ✓ CLO Equity: X new articles
  ✓ Secondary Private Equity: X new articles
  ...
```

### 4. Check Output

Open `output/digest_YYYYMMDD_HHMMSS.html` in your browser to see the digest!

### 5. Enable Email Sending

Once you've verified it works:

```bash
# Edit .env and remove or set to false
SKIP_EMAIL_SEND=false
```

Then run again:
```bash
python monitor.py
```

## Schedule Daily Runs

### macOS/Linux (cron)

```bash
# Edit crontab
crontab -e

# Add this line (runs daily at 8 AM)
0 8 * * * cd /path/to/market-monitoring && python monitor.py
```

### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger: Daily at 8:00 AM
4. Action: Start a program
   - Program: `python.exe`
   - Arguments: `monitor.py`
   - Start in: `C:\path\to\market-monitoring`

## View Sample Digest

Open `output/sample_digest.html` in your browser to see what the email will look like!

## Troubleshooting

**No articles found?**
- Wait a few hours (Google News updates periodically)
- Check your internet connection
- Try a different network if on corporate WiFi

**Email not sending?**
- Make sure you're using a Gmail App Password (not regular password)
- Verify 2-Factor Authentication is enabled on Google account
- Check SMTP credentials in .env file

**Module not found?**
```bash
pip install -r requirements.txt
```

## What's Next?

- Customize keywords in `config.py`
- Add more priority funds in `config.py`
- Adjust time periods and thresholds in `config.py`
- Schedule daily runs with cron or Task Scheduler

---

**Need Help?** Check the full README.md for detailed documentation.
