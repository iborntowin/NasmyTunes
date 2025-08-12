# 🔧 Troubleshooting Guide

## Common Deployment Issues

### 1. **Build Failures**
**Problem:** Render build fails
**Solutions:**
- Check if `requirements.txt` is in root directory
- Ensure Python version compatibility
- Check Render build logs

### 2. **FFmpeg Not Found**
**Problem:** Audio conversion fails
**Solutions:**
- Add to `requirements.txt`: `ffmpeg-python`
- Or use system package in build command

### 3. **Environment Variables**
**Problem:** API calls fail
**Check:**
- All env vars are set in Render dashboard
- No extra spaces in values
- Spotify credentials are valid

### 4. **Timeout Issues**
**Problem:** Conversion takes too long
**Solutions:**
- Render free tier has 15-minute timeout
- Test with smaller playlists first
- Consider upgrading to paid plan for longer processes

### 5. **CORS Errors**
**Problem:** Frontend can't connect to API
**Solution:** Already handled with `flask-cors`

## Testing Checklist

✅ Website loads
✅ Can paste Spotify URL
✅ Playlist analysis works
✅ YouTube search works
✅ Conversion starts
✅ Progress updates
✅ Download works

## Performance Tips

- Start with 2-3 song playlists for testing
- Larger playlists may timeout on free tier
- Monitor Render logs for errors
- Use public Spotify playlists only