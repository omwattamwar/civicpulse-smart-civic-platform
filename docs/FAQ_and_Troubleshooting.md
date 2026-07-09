# FAQ & Troubleshooting

## Common Issues

### 1. Missing API Keys
**Symptom:** AI features (categorization, summarization) are failing.
**Fix:** Ensure your `.env` file has a valid `VITE_GEMINI_API_KEY`.

### 2. Microservice Connection Refused
**Symptom:** Image uploads and YOLO vision detection are failing.
**Fix:** Ensure the FastAPI server is running on `http://localhost:8000` before starting the frontend.

### 3. Firebase Auth Errors
**Symptom:** Cannot log in or register.
**Fix:** Verify that Firebase Authentication (Email/Password provider) is enabled in your Firebase console.

### 4. CORS Errors on API
**Symptom:** Network requests to the Python API fail from the browser.
**Fix:** Ensure `CORSMiddleware` in `main.py` is configured to allow `http://localhost:5173`.
