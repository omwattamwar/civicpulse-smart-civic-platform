# Environment Variables Guide

The CivicPulse platform requires multiple environment variables for both the React frontend and the Python AI microservice.

## Frontend (`.env` in root directory)

```env
# Google Gemini API for NLP (Text analysis, Categorization, Summarization)
VITE_GEMINI_API_KEY=your_gemini_api_key_here

# Firebase Configuration for Authentication and Firestore
VITE_FIREBASE_API_KEY=your_firebase_api_key
VITE_FIREBASE_AUTH_DOMAIN=your_project.firebaseapp.com
VITE_FIREBASE_PROJECT_ID=your_project_id
VITE_FIREBASE_STORAGE_BUCKET=your_project.appspot.com
VITE_FIREBASE_MESSAGING_SENDER_ID=your_sender_id
VITE_FIREBASE_APP_ID=your_app_id

# Cloudinary for Image Uploads
VITE_CLOUDINARY_UPLOAD_PRESET=your_upload_preset
VITE_CLOUDINARY_CLOUD_NAME=your_cloud_name
```

## AI Microservice (`ai-microservice/.env`)

```env
# Google Gemini API (if used server-side)
GEMINI_API_KEY=your_gemini_api_key_here

# Power BI Integration
POWERBI_API_KEY=your_powerbi_api_key_here
```

## AI Microservice Firebase Credentials

In addition to `.env`, the AI microservice requires a Service Account Key to interact with Firestore server-side.

Place your JSON key at `ai-microservice/firebase_config.json`:

```json
{
  "type": "service_account",
  "project_id": "your-project-id",
  "private_key_id": "...",
  "private_key": "-----BEGIN PRIVATE KEY-----\n...\n-----END PRIVATE KEY-----\n",
  "client_email": "...",
  "client_id": "...",
  "auth_uri": "https://accounts.google.com/o/oauth2/auth",
  "token_uri": "https://oauth2.googleapis.com/token",
  "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
  "client_x509_cert_url": "..."
}
```

> **Warning:** Never commit your `.env` or `firebase_config.json` files to version control! They are included in `.gitignore` by default.
