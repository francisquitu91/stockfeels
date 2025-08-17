# Deployment Guide

## Streamlit Community Cloud (Recommended)

### Prerequisites
1. Push your code to GitHub
2. Create a Streamlit Community Cloud account at https://share.streamlit.io/

### Steps:
1. **Prepare your repository:**
   - Ensure `requirements.txt` is up to date
   - Add `.streamlit/config.toml` for theme configuration
   - Create `app.py` as your main entry point

2. **Deploy on Streamlit Cloud:**
   - Go to https://share.streamlit.io/
   - Click "New app"
   - Connect your GitHub repository
   - Set main file path to `app.py`
   - Add secrets in the Streamlit Cloud dashboard

3. **Configure Secrets:**
   - In Streamlit Cloud dashboard, go to your app settings
   - Add secrets in the "Secrets" section:
   ```toml
   OPENAI_API_KEY = "your-actual-key"
   FIRECRAWL_API_KEY = "your-actual-key"
   ```

## Alternative Deployment Options

### 1. Heroku
- Create `Procfile`: `web: streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`
- Add buildpacks for Python
- Configure environment variables

### 2. Railway
- Connect GitHub repository
- Set start command: `streamlit run app.py`
- Configure environment variables

### 3. Render
- Connect GitHub repository
- Set build command: `pip install -r requirements.txt`
- Set start command: `streamlit run app.py --server.port=$PORT --server.address=0.0.0.0`

### 4. Google Cloud Run
- Create Dockerfile
- Build and deploy container
- Configure environment variables

## Important Notes

1. **Environment Variables:** Never commit API keys to your repository
2. **Dependencies:** Keep requirements.txt updated
3. **File Paths:** Use relative paths in your code
4. **Memory Usage:** Monitor your app's memory usage on the deployment platform
5. **API Limits:** Be aware of API rate limits for external services

## Troubleshooting

- Check logs in your deployment platform
- Ensure all dependencies are in requirements.txt
- Verify environment variables are set correctly
- Test locally before deploying