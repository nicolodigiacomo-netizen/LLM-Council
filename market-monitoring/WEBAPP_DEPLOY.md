# Web Application Deployment Guide

## Overview

The Financial News Monitoring System includes a modern web interface for managing and viewing collected news. This guide covers local and production deployment options.

## Features

✅ **User Authentication** - Secure login with password hashing
✅ **Dashboard** - Real-time statistics and recent articles
✅ **Manual Monitoring** - Run news collection with one click
✅ **Digest History** - View and download past email digests
✅ **Configuration View** - See current system settings
✅ **Test Tools** - Test news scraper directly from UI
✅ **Responsive Design** - Works on desktop, tablet, and mobile

---

## Quick Start (Local Development)

### 1. Install Dependencies

```bash
cd market-monitoring
pip install -r webapp_requirements.txt
```

### 2. Run the Application

```bash
python app.py
```

The application will start on `http://localhost:5000`

### 3. Login

**Default Credentials:**
- Username: `admin`
- Password: `admin123`

⚠️ **Important:** Change the default password after first login!

---

## Production Deployment

### Option 1: Deploy on Local Server/VPS

#### Using Gunicorn (Recommended)

```bash
# Install gunicorn
pip install gunicorn

# Run with gunicorn
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

**Options:**
- `-w 4`: Use 4 worker processes
- `-b 0.0.0.0:8000`: Bind to all interfaces on port 8000
- `app:app`: Module name and Flask app instance

#### Using Systemd (Linux)

Create `/etc/systemd/system/markets-monitor.service`:

```ini
[Unit]
Description=Private Markets Monitor Web App
After=network.target

[Service]
User=your-username
WorkingDirectory=/path/to/market-monitoring
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:8000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:
```bash
sudo systemctl daemon-reload
sudo systemctl enable markets-monitor
sudo systemctl start markets-monitor
```

### Option 2: Deploy on Heroku

#### Prepare for Heroku

Create `Procfile`:
```
web: gunicorn app:app
```

Create `runtime.txt`:
```
python-3.11.0
```

#### Deploy

```bash
# Install Heroku CLI
brew install heroku/brew/heroku  # macOS
# or download from https://devcenter.heroku.com/articles/heroku-cli

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key-here

# Deploy
git push heroku main

# Open app
heroku open
```

### Option 3: Deploy with Docker

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt webapp_requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt -r webapp_requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "app:app"]
```

Build and run:

```bash
# Build image
docker build -t markets-monitor .

# Run container
docker run -d -p 8000:8000 \
  -e SECRET_KEY=your-secret-key \
  -v $(pwd)/market_monitoring.db:/app/market_monitoring.db \
  -v $(pwd)/output:/app/output \
  markets-monitor
```

### Option 4: Deploy on Cloud Platforms

#### AWS Elastic Beanstalk

```bash
pip install awsebcli

eb init -p python-3.11 markets-monitor
eb create markets-monitor-env
eb deploy
```

#### Google Cloud Run

```bash
gcloud run deploy markets-monitor \
  --source . \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated
```

#### DigitalOcean App Platform

1. Push code to GitHub
2. Go to DigitalOcean → Apps → Create App
3. Connect GitHub repository
4. Select `market-monitoring` directory
5. Deploy!

---

## Configuration

### Environment Variables

Create `.env` file or set environment variables:

```bash
# Required for production
SECRET_KEY=your-secret-key-here-change-this

# Optional: Custom port
PORT=8000

# Email configuration (from main .env)
EMAIL_TO=your-email@gmail.com
SMTP_SERVER=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=your-email@gmail.com
SMTP_PASSWORD=your-app-password
SKIP_EMAIL_SEND=false
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

---

## Security Considerations

### 1. Change Default Credentials

After first login, create new users and remove or change the default admin account.

### 2. Use HTTPS

In production, always use HTTPS. Options:
- **Nginx reverse proxy** with Let's Encrypt SSL
- **Cloud platform** SSL (automatic on Heroku, AWS, etc.)
- **Cloudflare** for free SSL

Example Nginx configuration:

```nginx
server {
    listen 443 ssl;
    server_name your-domain.com;

    ssl_certificate /path/to/cert.pem;
    ssl_certificate_key /path/to/key.pem;

    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3. Firewall Rules

Only expose necessary ports:
- Port 80 (HTTP) → redirect to 443
- Port 443 (HTTPS)
- SSH (port 22) from trusted IPs only

### 4. User Management

Users are stored in `users.json`. For production:
- Consider moving to proper database (PostgreSQL, MySQL)
- Implement password reset functionality
- Add email verification
- Implement role-based access control (RBAC)

---

## Sharing with Team

### Option 1: Deploy and Share URL

1. Deploy to cloud platform (Heroku, AWS, etc.)
2. Share URL with team: `https://your-app.herokuapp.com`
3. Create accounts for team members

### Option 2: Local Network Sharing

If running on local server:

```bash
# Find your local IP
ifconfig  # macOS/Linux
ipconfig  # Windows

# Run app on all interfaces
python app.py

# Share URL with team: http://YOUR-IP:5000
```

### Option 3: Tunnel Service (for Testing)

Use ngrok for temporary public URL:

```bash
# Install ngrok
brew install ngrok  # macOS

# Run app
python app.py

# In another terminal
ngrok http 5000

# Share the ngrok URL (e.g., https://abc123.ngrok.io)
```

⚠️ **Note:** Ngrok free tier URLs expire. Use only for testing!

---

## Monitoring and Maintenance

### Check Application Status

```bash
# If using systemd
sudo systemctl status markets-monitor

# View logs
sudo journalctl -u markets-monitor -f
```

### Database Backup

```bash
# Backup database
cp market_monitoring.db market_monitoring.backup.$(date +%Y%m%d).db

# Automated daily backup
echo "0 2 * * * cp /path/to/market_monitoring.db /path/to/backups/market_monitoring.backup.\$(date +\%Y\%m\%d).db" | crontab -
```

### Update Application

```bash
git pull origin main
pip install -r webapp_requirements.txt
sudo systemctl restart markets-monitor  # if using systemd
```

---

## Troubleshooting

### Port Already in Use

```bash
# Find process using port 5000
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Kill process
kill -9 <PID>
```

### Permission Denied

```bash
# Ensure database is writable
chmod 666 market_monitoring.db
chmod 777 output/
```

### Cannot Access from Other Devices

- Check firewall rules
- Ensure app binds to `0.0.0.0` not `127.0.0.1`
- Verify network connectivity

---

## Performance Optimization

### For Production

1. **Use Gunicorn with multiple workers:**
   ```bash
   gunicorn -w $(nproc) -b 0.0.0.0:8000 app:app
   ```

2. **Enable caching:**
   - Use Redis for session storage
   - Cache static files with CDN

3. **Database optimization:**
   - Regular VACUUM on SQLite
   - Consider PostgreSQL for high traffic

4. **Monitoring:**
   - Use Sentry for error tracking
   - Set up uptime monitoring (UptimeRobot, Pingdom)

---

## Advanced: Multi-Tenant Setup

To support multiple organizations:

1. **Separate databases per tenant:**
   ```python
   DB_PATH = f"market_monitoring_{tenant_id}.db"
   ```

2. **Subdomain routing:**
   - `company1.your-domain.com`
   - `company2.your-domain.com`

3. **Shared deployment with tenant isolation**

---

## Support

- **Documentation:** See README.md and QUICK_START.md
- **Issues:** Check logs in `monitoring.log`
- **Updates:** Pull latest from Git repository

---

**Ready to deploy!** Choose your deployment method above and get started. 🚀

For questions or issues, refer to the main README.md or contact your system administrator.
