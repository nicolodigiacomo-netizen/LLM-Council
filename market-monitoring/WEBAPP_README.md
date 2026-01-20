# Web Application - Quick Start Guide

## 🌐 Private Markets Monitor - Web Interface

Modern web dashboard for the Financial News Monitoring System.

---

## 🚀 Quick Start (60 seconds)

```bash
# 1. Install dependencies
pip install -r webapp_requirements.txt

# 2. Run the application
python app.py

# 3. Open browser
# Visit: http://localhost:5000

# 4. Login
# Username: admin
# Password: admin123
```

**That's it!** You now have a running web application.

---

## 📱 Features

### Dashboard
- Real-time statistics
- Recent articles by priority
- One-click monitoring execution
- Visual priority indicators

### Articles View
- Browse all collected articles
- Filter by priority, asset class, time range
- Direct links to sources
- Keyword and fund tags

### Digest History
- View past email digests
- Download HTML reports
- Searchable archive

### Configuration
- View current settings
- Asset class configuration
- Priority fund list
- Test news scraper

### User Management
- Secure authentication
- Multi-user support
- Password hashing
- Session management

---

## 🎨 Screenshots

```
┌─────────────────────────────────────────┐
│  🏠 Dashboard                           │
├─────────────────────────────────────────┤
│  📊 Statistics Cards                    │
│  ├─ Total Articles: 125                 │
│  ├─ Last 24h: 15                        │
│  ├─ Priority 1: 5                       │
│  └─ Priority 2: 3                       │
│                                          │
│  🔴 Priority 1 - Key Funds              │
│  ├─ Vista Equity closes $16.4B fund     │
│  ├─ BC Partners acquires healthcare...  │
│  └─ Hamilton Lane reports record...     │
│                                          │
│  [▶ Run Monitoring Now]                 │
└─────────────────────────────────────────┘
```

---

## 👥 User Management

### Register New User

```bash
# Method 1: Via Web Interface
1. Click "Register" on login page
2. Enter username, email, password
3. Login with new credentials

# Method 2: Via Python
python -c "
from app import load_users, save_users
from werkzeug.security import generate_password_hash
from datetime import datetime

users = load_users()
users['your-username'] = {
    'password': generate_password_hash('your-password'),
    'email': 'your@email.com',
    'created_at': datetime.now().isoformat()
}
save_users(users)
print('User created!')
"
```

### Change Password

```bash
python -c "
from app import load_users, save_users
from werkzeug.security import generate_password_hash

users = load_users()
users['username']['password'] = generate_password_hash('new-password')
save_users(users)
print('Password updated!')
"
```

---

## 🔧 Configuration

### Environment Variables

Create `.env` or set environment variables:

```bash
# Required for production
SECRET_KEY=your-secret-key-here

# Optional
PORT=5000

# Generate secret key:
python -c "import secrets; print(secrets.token_hex(32))"
```

### Custom Port

```bash
# Option 1: Environment variable
export PORT=8000
python app.py

# Option 2: Command line
PORT=8000 python app.py

# Option 3: Edit app.py
# Change: port = int(os.environ.get('PORT', 5000))
# To:     port = int(os.environ.get('PORT', 8000))
```

---

## 🌍 Deployment Options

### Local Network Access

```bash
# Run on all interfaces
python app.py
# App accessible at: http://YOUR-LOCAL-IP:5000
```

### Production with Gunicorn

```bash
gunicorn -w 4 -b 0.0.0.0:8000 app:app
```

### Docker

```bash
docker build -t markets-monitor .
docker run -p 8000:8000 markets-monitor
```

### Cloud Platforms

See **WEBAPP_DEPLOY.md** for detailed deployment guides:
- Heroku
- AWS
- Google Cloud
- DigitalOcean
- Custom VPS

---

## 🔒 Security

### Production Checklist

- [ ] Change default admin password
- [ ] Set strong SECRET_KEY
- [ ] Enable HTTPS
- [ ] Configure firewall
- [ ] Regular database backups
- [ ] Update dependencies regularly

### HTTPS Setup (Nginx)

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
    }
}
```

---

## 🐛 Troubleshooting

### App Won't Start

```bash
# Check port availability
lsof -i :5000  # macOS/Linux
netstat -ano | findstr :5000  # Windows

# Check dependencies
pip install -r webapp_requirements.txt

# Check for errors
python app.py
```

### Can't Login

```bash
# Reset admin password
python -c "
from app import load_users, save_users
from werkzeug.security import generate_password_hash

users = load_users()
users['admin']['password'] = generate_password_hash('admin123')
save_users(users)
print('Admin password reset to: admin123')
"
```

### Database Errors

```bash
# Ensure database exists
python test_populate.py

# Fix permissions
chmod 666 market_monitoring.db
chmod 777 output/
```

---

## 📊 API Endpoints

The webapp exposes several API endpoints:

```
GET  /                      - Dashboard
GET  /login                 - Login page
POST /login                 - Login action
GET  /register              - Registration page
POST /register              - Register action
GET  /articles              - Articles list
GET  /digests               - Digest history
GET  /digest/<filename>     - View specific digest
POST /run-monitoring        - Execute monitoring
GET  /config                - Configuration view
GET  /api/stats             - Statistics JSON
POST /api/test-scraper      - Test scraper endpoint
```

---

## 🎯 Integration with Main System

The webapp integrates seamlessly with the CLI monitoring system:

```bash
# Run via CLI (scheduled with cron)
python monitor.py

# Or run via Web UI (manual execution)
# Click "Run Monitoring Now" button

# Both methods:
# - Use same database
# - Generate same digests
# - Send same emails
# - Store same data
```

---

## 💡 Tips & Best Practices

### 1. Regular Monitoring

Set up automated monitoring via cron:
```bash
0 8 * * * cd /path/to/market-monitoring && python monitor.py
```

Access webapp anytime to view results.

### 2. Team Collaboration

- Create separate accounts for team members
- Share deployment URL
- Use priority filters to focus on relevant news

### 3. Mobile Access

The webapp is fully responsive:
- Works on phones and tablets
- Touch-friendly interface
- Optimized for small screens

### 4. Backup Strategy

```bash
# Daily database backup
0 2 * * * cp /path/to/market_monitoring.db /backups/db_$(date +\%Y\%m\%d).db
```

---

## 📚 Documentation

- **WEBAPP_DEPLOY.md** - Detailed deployment guide
- **README.md** - Main system documentation
- **QUICK_START.md** - CLI quick start guide
- **INSTALLAZIONE.md** - Installation guide for end users

---

## 🆘 Support

### Common Issues

1. **Port in use:** Change PORT in .env or use different port
2. **Can't access remotely:** Bind to 0.0.0.0 instead of 127.0.0.1
3. **Slow performance:** Use gunicorn with multiple workers
4. **Database locked:** Ensure only one monitoring process runs

### Getting Help

1. Check logs: `monitoring.log`
2. Test scraper via Config page
3. Verify database: `python test_populate.py`
4. Review documentation

---

## 🎉 You're All Set!

The webapp is ready to use. Start with:

```bash
python app.py
```

Then visit `http://localhost:5000` and explore the interface!

For production deployment, see **WEBAPP_DEPLOY.md**.

---

**Built with ❤️ for Private Markets professionals**
