# Deploy to Render Instructions

1. Go to: https://dashboard.render.com/new/web
2. Connect your GitHub account if not already connected
3. Select the repository: `alphagenome-backend`
4. Use these settings:
   - Name: `alphagenome-backend`
   - Environment: `Python`
   - Build Command: `pip install -r requirements.txt`
   - Start Command: `gunicorn app:app`
   
5. Add Environment Variables:
   - `ALPHAGENOME_API_KEY` = `AIzaSyAd8VEbbDBGpQoPGK4v8LZzdaGlgBh2kaE`
   - `PYTHON_VERSION` = `3.11.0`

6. Click "Create Web Service"

The service will be available at: https://alphagenome-backend.onrender.com