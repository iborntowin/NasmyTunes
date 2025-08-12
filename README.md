# 🎵 Spotify to MP3 Converter

Convert your Spotify playlists to high-quality MP3 files with a beautiful glassmorphism interface.

## ⚡ Quick Start

1. **Clone the repository:**
```bash
git clone <your-repo-url>
cd spotify-mp3-converter
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Install FFmpeg:**
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

4. **Set up environment variables:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

5. **Get API Keys:**
   - **Spotify:** [Developer Dashboard](https://developer.spotify.com/dashboard)
   - **Genius (optional):** [API Clients](https://genius.com/api-clients)

6. **Run locally:**
```bash
python src/main.py
```

## 🚀 Free Deployment Options

### Railway (Recommended)
- $5/month free credits
- Easy GitHub integration
- Automatic deployments

### Render
- 100% free tier
- 750 hours/month
- Simple setup

### Vercel
- Free with limitations
- Great for demos

## 🔒 Security

- Never commit `.env` files
- Use platform environment variables for deployment
- Regenerate API keys if accidentally exposed

## ⚖️ Legal

This tool is for **personal use only**. Respect copyright laws and platform terms of service.

## 🛠️ Features

- ✅ Spotify playlist analysis
- ✅ YouTube audio search & download
- ✅ High-quality MP3 conversion (192kbps)
- ✅ Batch processing with progress tracking
- ✅ ZIP file downloads
- ✅ Modern glassmorphism UI
- ✅ Mobile responsive

## 📱 Usage

1. Paste a public Spotify playlist URL
2. Preview tracks
3. Start conversion
4. Download ZIP file with MP3s

Enjoy your music! 🎶