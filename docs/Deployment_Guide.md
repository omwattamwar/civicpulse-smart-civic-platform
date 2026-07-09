# Deployment Guide

## Deploying the Frontend (Vercel / Netlify / Firebase Hosting)

The frontend is a static React/Vite build.

1. Build the app:
   ```bash
   npm run build
   ```
2. The compiled assets will be in the `dist/` directory.
3. If using Vercel or Netlify, simply connect your GitHub repository and set the build command to `npm run build` and output directory to `dist`.

## Deploying the AI Microservice (Render / Heroku / GCP)

The FastAPI microservice can be deployed to any platform supporting Python Docker containers or ASGI apps.

1. Create a `Procfile` (if using Heroku/Render):
   ```text
   web: uvicorn main:app --host 0.0.0.0 --port $PORT
   ```
2. Ensure you add your `GEMINI_API_KEY`, `POWERBI_API_KEY`, and all Firebase service account variables to the deployment environment secrets.
3. Start the server.
