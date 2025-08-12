# 🎵 NasmyTunes - Spotify to MP3 Converter

Convert your Spotify playlists to high-quality MP3 files with an easy-to-use CLI interface.

## 🚀 Super Quick Start

```bash
git clone https://github.com/iborntowin/NasmyTunes.git
cd NasmyTunes
python setup.py
# Edit .env with your Spotify API credentials
python nasmytunes_cli.py  # Or double-click nasmytunes.bat on Windows
```

That's it! Just paste your playlist URL and enjoy your music! 🎵

## 📋 Table of Contents

- [🏗️ System Architecture](#️-system-architecture)
- [⚡ Quick Start](#-quick-start)
- [🌐 Live Demo](#-live-demo)
- [🚀 Free Deployment Options](#-free-deployment-options)
- [🤖 Advanced Bypass Techniques](#-advanced-bypass-techniques)
- [🛠️ Features](#️-features)
- [🔒 Security](#-security)
- [⚖️ Legal](#️-legal)

## 🏗️ System Architecture

![NasmyTunes Architecture](diagram.png)

*Complete system architecture showing the flow from Spotify playlist analysis to MP3 conversion and download*

## ⚡ Quick Start

### 🖥️ CLI Version (Recommended)

1. **Clone and setup:**
```bash
git clone https://github.com/iborntowin/NasmyTunes.git
cd NasmyTunes
python setup.py  # Automatically installs everything!
```

2. **Configure Spotify API:**
   - Edit `.env` with your [Spotify API credentials](https://developer.spotify.com/dashboard)

3. **Start the app:**
```bash
# Windows - Double-click nasmytunes.bat
# Or run: python nasmytunes_cli.py

# Mac/Linux  
./nasmytunes.sh
```

4. **Use the menu:**
   - Select option 1 to convert playlists
   - Just paste your Spotify playlist URL
   - Choose your preferences
   - Done! 🎉

### 🌐 Web Version

1. **Manual setup:**
```bash
git clone <your-repo-url>
cd spotify-mp3-converter
pip install -r requirements.txt
```

2. **Install FFmpeg:**
   - Windows: `winget install ffmpeg`
   - macOS: `brew install ffmpeg`
   - Linux: `sudo apt install ffmpeg`

3. **Configure environment:**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run locally:**
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

## 🌐 Live Demo

**🚀 Try it now:** [https://nasmytunes.onrender.com](https://nasmytunes.onrender.com)

### 📱 How to Use

1. **🎵 Paste Spotify playlist URL** (make sure it's public)
2. **👀 Preview tracks** and confirm selection  
3. **🚀 Start conversion** with real-time progress
4. **📦 Download ZIP** with converted files

## 🏗️ Technical Architecture

The diagram above shows our comprehensive system design featuring:

- **🎯 Multi-layer Bypass System**: Advanced techniques to handle YouTube's bot detection
- **🔄 Real-time Processing**: Live progress updates and status tracking
- **🛡️ Graceful Degradation**: Demo mode when cloud restrictions apply
- **📊 Professional UI**: Modern glassmorphism design with responsive layout

📚 **Documentation:**
- [Architecture Guide](docs/ARCHITECTURE.md) - Technical deep dive
- [Visual Guide](docs/VISUAL_GUIDE.md) - Diagram breakdown and UI/UX details

## 🤖 Advanced Bypass Techniques

Our system implements cutting-edge bypass methods:

- **🔐 Authentication Simulation**: Browser cookie management
- **📱 Multiple Client Types**: Android, Web, Embedded clients
- **🌐 Rate Limiting**: Human-like request patterns
- **🔄 Proxy Support**: IP rotation capabilities
- **🎯 Fallback Systems**: Graceful handling of failures

## 🎉 Why NasmyTunes?

- **✨ Works Locally**: Full MP3 downloads on your computer
- **🌐 Cloud Demo**: Professional demonstration on Render
- **🔧 Open Source**: Complete codebase available
- **📚 Educational**: Learn about API integration and bypass techniques
- **🎨 Modern Design**: Beautiful glassmorphism interface

Enjoy your music! 🎶