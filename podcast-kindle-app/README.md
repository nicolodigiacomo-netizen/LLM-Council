# 🎙️ Podcast to Kindle

Transform English podcast transcripts into beautifully formatted narrative ebooks for your Kindle.

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.11-blue.svg)
![Flask](https://img.shields.io/badge/flask-3.0-green.svg)

## ✨ Features

- 🔍 **Search English podcasts** using multiple free APIs (iTunes, Podcast Index, Listen Notes)
- 📝 **Free transcripts only** - automatically filters episodes with available transcripts
- 📖 **Narrative transformation** - converts conversational transcripts to readable prose
- 📚 **EPUB & PDF generation** - optimized for Kindle reading
- 🌐 **Web-based** - no installation required for users
- 🚀 **Free deployment** - deploy on Render or Railway
- 💾 **Smart caching** - reduces API calls and improves performance

## 🎯 Key Capabilities

### Transcript Sources
- YouTube transcripts (via youtube-transcript-api)
- Podcast Index transcripts
- RSS feed embedded transcripts

### Text Transformation
- Removes filler words (um, uh, you know, like)
- Eliminates timestamps and speaker labels
- Converts to narrative prose
- Organizes into thematic chapters
- Extracts key takeaways
- Preserves examples and frameworks

## 🚀 Quick Start

### Prerequisites

- Python 3.11+
- Git
- (Optional) Podcast Index API credentials for better results

### Local Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd podcast-kindle-app
```

2. **Create virtual environment**
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install dependencies**
```bash
pip install -r requirements.txt
```

4. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` and add your API keys:
```env
# Podcast Index API (Recommended - Free with registration)
PODCAST_INDEX_KEY=your_key_here
PODCAST_INDEX_SECRET=your_secret_here

# Listen Notes API (Optional)
LISTEN_NOTES_KEY=optional

# Flask Configuration
FLASK_SECRET_KEY=your-random-secret-key
FLASK_ENV=development
```

5. **Run the application**
```bash
python app.py
```

Visit `http://localhost:5000` in your browser.

## 🔑 Getting API Keys

### Podcast Index API (Recommended - Free)

1. Visit [https://podcastindex.org](https://podcastindex.org)
2. Click "Get API Key" in the top right
3. Fill out the simple form (no credit card required)
4. You'll receive your API Key and Secret immediately
5. Add them to your `.env` file

**Benefits:**
- Completely free
- Access to transcript data
- Better search results
- No rate limits for reasonable use

### iTunes Search API

No API key required! Works out of the box.

### Listen Notes API (Optional)

1. Visit [https://www.listennotes.com/api/](https://www.listennotes.com/api/)
2. Sign up for free tier (10,000 requests/month)
3. Add API key to `.env` file

**Note:** iTunes API is sufficient for most use cases. Listen Notes is optional.

## 🌐 Deployment

### Deploy on Render (Recommended)

1. **Push your code to GitHub**

2. **Create Render account**
   - Go to [https://render.com](https://render.com)
   - Sign up with GitHub

3. **Create new Web Service**
   - Click "New +" → "Web Service"
   - Connect your GitHub repository
   - Render will auto-detect the `render.yaml` configuration

4. **Set environment variables**
   - In Render dashboard, go to "Environment"
   - Add your API keys:
     - `PODCAST_INDEX_KEY`
     - `PODCAST_INDEX_SECRET`
     - `FLASK_SECRET_KEY` (generate random string)
     - `FLASK_ENV=production`

5. **Deploy**
   - Click "Create Web Service"
   - Render will automatically deploy your app
   - You'll get a URL like `https://your-app.onrender.com`

**Free Tier Limits:**
- App sleeps after 15 minutes of inactivity
- Wakes up automatically when accessed (takes ~30 seconds)
- 750 hours/month of runtime (plenty for personal use)

### Deploy on Railway

1. **Push code to GitHub**

2. **Create Railway account**
   - Go to [https://railway.app](https://railway.app)
   - Sign up with GitHub

3. **Deploy**
   - Click "New Project" → "Deploy from GitHub repo"
   - Select your repository
   - Railway auto-detects Python and uses `railway.json`

4. **Set environment variables**
   - Go to "Variables" tab
   - Add your API keys (same as Render)

5. **Generate domain**
   - Go to "Settings" → "Generate Domain"
   - Your app will be live at the generated URL

**Free Tier:**
- $5 credit/month (sufficient for moderate use)
- No sleep/wake delays

## 📖 How to Use

### 1. Search for Podcasts

- Enter keywords (e.g., "persuasion", "sales", "psychology")
- Or use quick filter buttons
- Results show only podcasts with available transcripts

### 2. Select Episodes

- Click on a podcast to see episodes
- Only episodes with transcripts are selectable
- Select one or multiple episodes (max 5 per session)

### 3. Process & Preview

- Click "Process & Preview"
- Transcripts are transformed to narrative format
- Preview the content before downloading

### 4. Download for Kindle

- Choose format (EPUB recommended)
- Download the file
- Send to your Kindle (see instructions below)

## 📱 Sending to Kindle

### Method 1: Email (Easiest)

1. Find your Kindle email at: Amazon Account → Content & Devices → Preferences → Personal Document Settings
2. Your Kindle email looks like: `yourname@kindle.com`
3. Email the EPUB file as attachment to this address
4. Document appears on your Kindle within minutes

### Method 2: Send to Kindle App

1. Download "Send to Kindle" app from Amazon
2. Right-click downloaded file → Send to Kindle

### Method 3: USB Transfer

1. Connect Kindle via USB
2. Copy file to "Documents" folder
3. Safely eject

## 🛠️ Technical Architecture

```
podcast-kindle-app/
├── app.py                 # Flask application
├── requirements.txt       # Python dependencies
├── .env.example          # Environment variables template
├── src/
│   ├── search.py         # Podcast search (iTunes, Podcast Index)
│   ├── transcript.py     # Free transcript retrieval
│   ├── transform.py      # Narrative transformation
│   ├── ebook.py          # EPUB/PDF generation
│   └── utils.py          # Helper functions
├── static/
│   ├── css/style.css     # Minimal, clean design
│   └── js/app.js         # Frontend logic
├── templates/
│   ├── base.html         # Base template
│   └── index.html        # Main page (SPA-style)
└── downloads/            # Temporary file storage
```

### Technologies

**Backend:**
- Flask 3.0 - Web framework
- youtube-transcript-api - YouTube transcripts
- ebooklib - EPUB generation
- feedparser - RSS parsing
- BeautifulSoup4 - HTML parsing

**Frontend:**
- Vanilla JavaScript (no frameworks)
- Clean, minimal CSS
- Fully responsive design

## ⚙️ Configuration

### Environment Variables

```env
# API Keys
PODCAST_INDEX_KEY=your_key          # Podcast Index API key
PODCAST_INDEX_SECRET=your_secret    # Podcast Index API secret
LISTEN_NOTES_KEY=optional           # Listen Notes API key (optional)

# Flask
FLASK_SECRET_KEY=random-secret      # Generate with: python -c "import secrets; print(secrets.token_hex(32))"
FLASK_ENV=production                # development or production

# Rate Limiting
MAX_EPISODES_PER_SESSION=5          # Max episodes per session (default: 5)
CACHE_DURATION_HOURS=24             # Cache duration (default: 24)
PROCESSING_TIMEOUT_MINUTES=2        # Max processing time (default: 2)
```

### Generate Secret Key

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

## 🧪 Testing

### Test Locally

```bash
# Run the development server
python app.py

# Visit http://localhost:5000
# Try searching for: "lex fridman" or "huberman lab"
# (These podcasts often have transcripts)
```

### Test Known Working Podcasts

These podcasts typically have transcripts available:
- Lex Fridman Podcast
- Huberman Lab
- The Tim Ferriss Show
- The Knowledge Project
- All-In Podcast
- My First Million

## 🐛 Troubleshooting

### "No episodes with transcripts found"

**Causes:**
- Podcast doesn't provide transcripts
- Transcripts not in supported formats
- YouTube videos not linked

**Solutions:**
- Try different podcasts (use examples above)
- Check if podcast has YouTube versions
- Enable Podcast Index API for better results

### "Search failed" or API errors

**Causes:**
- API credentials incorrect
- Rate limits exceeded
- Network issues

**Solutions:**
- Verify API keys in `.env` file
- Check API key format (no quotes, spaces)
- Wait a few minutes if rate limited
- iTunes API always works without credentials

### "Processing timeout"

**Causes:**
- Transcript too long
- Server resources limited

**Solutions:**
- Select fewer episodes at once
- Choose shorter episodes
- Increase timeout in `.env` (if self-hosting)

### Files not downloading

**Causes:**
- Browser blocking download
- Downloads folder permissions

**Solutions:**
- Check browser console for errors
- Ensure downloads/ folder is writable
- Try different browser

### App sleeping on Render

**Cause:** Free tier sleeps after 15 minutes inactivity

**Solution:** Wait 30 seconds for app to wake up. This is normal for free tier.

## 📊 Limitations

### Free Tier Constraints

- **Transcripts:** Only episodes with existing free transcripts
- **Rate Limits:** 5 episodes per session (prevents abuse)
- **Processing Time:** 2 minutes max per episode
- **File Storage:** Temporary files deleted after 24 hours

### API Limitations

- **iTunes:** No rate limits (free)
- **Podcast Index:** Reasonable use (free)
- **Listen Notes:** 10,000 requests/month (free tier)
- **YouTube:** ~100 requests/day per IP (generous)

## 🔒 Security

- Input sanitization for all user data
- Rate limiting to prevent abuse
- CORS configured correctly
- No sensitive data storage
- Temporary files with random names
- Automatic cleanup of old files

## 🤝 Contributing

Contributions welcome! Areas for improvement:

- Better chapter detection (NLP/ML)
- More transcript sources
- PDF generation (proper library)
- Batch processing
- User accounts
- Favorite podcasts
- Advanced text transformations

## 📝 License

MIT License - See LICENSE file for details

## 🙏 Acknowledgments

- iTunes Search API
- Podcast Index
- Listen Notes
- YouTube Transcript API
- All open-source libraries used

## 📧 Support

For issues and questions:
1. Check [Troubleshooting](#-troubleshooting) section
2. Search existing GitHub issues
3. Create new issue with details

## 🗺️ Roadmap

- [ ] Improved NLP for chapter organization
- [ ] Support for more podcast platforms
- [ ] Multiple transcript sources fallback
- [ ] User preferences (font, spacing)
- [ ] Epub validation
- [ ] Better cover image handling
- [ ] Progress tracking for long processes
- [ ] Export to other formats (MOBI, AZW3)

---

Made with ❤️ for podcast lovers and Kindle readers
