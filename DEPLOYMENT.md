# YourCarePal Deployment Guide

This guide provides multiple deployment options for your YourCarePal Streamlit application.

## 🚀 Quick Deployment Options

### Option 1: Streamlit Cloud (Recommended - Free)

1. **Push to GitHub:**
   ```bash
   git init
   git add .
   git commit -m "Initial commit"
   git branch -M main
   git remote add origin https://github.com/yourusername/yourcarepal.git
   git push -u origin main
   ```

2. **Deploy on Streamlit Cloud:**
   - Go to [share.streamlit.io](https://share.streamlit.io)
   - Sign in with GitHub
   - Click "New app"
   - Select your repository
   - Set main file path: `app.py`
   - Add environment variables:
     - `OPENAI_API_KEY`: Your OpenAI API key (optional)

### Option 2: Heroku

1. **Install Heroku CLI:**
   ```bash
   # macOS
   brew install heroku/brew/heroku
   
   # Or download from https://devcenter.heroku.com/articles/heroku-cli
   ```

2. **Deploy:**
   ```bash
   # Login to Heroku
   heroku login
   
   # Create app
   heroku create yourcarepal-app
   
   # Set environment variables
   heroku config:set OPENAI_API_KEY=your_api_key_here
   
   # Deploy
   git push heroku main
   ```

### Option 3: Railway

1. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   ```

2. **Deploy:**
   ```bash
   railway login
   railway init
   railway up
   ```

### Option 4: Docker Deployment

1. **Build and run locally:**
   ```bash
   # Build the Docker image
   docker build -t yourcarepal .
   
   # Run the container
   docker run -p 8501:8501 -e OPENAI_API_KEY=your_key_here yourcarepal
   ```

2. **Using Docker Compose:**
   ```bash
   # Copy env.example to .env and add your API key
   cp env.example .env
   
   # Edit .env file with your API key
   nano .env
   
   # Run with docker-compose
   docker-compose up -d
   ```

### Option 5: Local Development

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run locally:**
   ```bash
   streamlit run app.py
   ```

3. **Access:** http://localhost:8501

## 🔧 Configuration

### Environment Variables

- `OPENAI_API_KEY`: Your OpenAI API key (optional - app works offline without it)

### Streamlit Configuration

The app includes optimized Streamlit configuration in `.streamlit/config.toml`:
- Headless mode for deployment
- CORS disabled
- XSRF protection disabled
- Usage stats disabled

## 📱 Features

- **Offline Mode**: Works without API keys using rule-based responses
- **AI Mode**: Enhanced responses with OpenAI integration
- **Emergency Detection**: Automatic emergency response system
- **Philippine Context**: Localized health advice and nutrition
- **Multiple Personas**: Clinic Nurse, Health Coach, School Counselor

## 🛠️ Troubleshooting

### Common Issues

1. **Port already in use:**
   ```bash
   # Kill process using port 8501
   lsof -ti:8501 | xargs kill -9
   ```

2. **OpenAI API errors:**
   - Check your API key
   - Ensure you have credits in your OpenAI account
   - App will fallback to offline mode if API fails

3. **Docker build issues:**
   ```bash
   # Clean Docker cache
   docker system prune -a
   ```

### Health Checks

- **Local**: http://localhost:8501/_stcore/health
- **Docker**: http://localhost:8501/_stcore/health

## 🔒 Security Notes

- The app includes an embedded API key for demo purposes
- For production, use environment variables
- Never commit API keys to version control
- Use `.env` files for local development

## 📊 Monitoring

- Streamlit provides built-in metrics
- Check application logs in your deployment platform
- Monitor API usage if using OpenAI integration

## 🚀 Production Recommendations

1. **Use environment variables** for API keys
2. **Enable HTTPS** in production
3. **Set up monitoring** and logging
4. **Use a proper domain** instead of default URLs
5. **Implement rate limiting** if needed
6. **Regular backups** of any persistent data

## 📞 Support

For deployment issues:
1. Check the logs in your deployment platform
2. Verify environment variables are set correctly
3. Ensure all dependencies are installed
4. Test locally first before deploying

---

**Built for CPELE230 Finals by Red Ocampo — Your Care Pal** 🩺
