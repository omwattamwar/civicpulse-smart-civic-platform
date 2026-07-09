# Installation Guide

Follow these steps to set up the CivicPulse platform locally.

## Prerequisites

- **Node.js** (v18.x or higher)
- **Python** (v3.10 or higher)
- **Git**
- A Google Cloud / Firebase account
- A Gemini API Key
- A Cloudinary account (for image hosting)

## 1. Clone the Repository

```bash
git clone https://github.com/your-username/civicpulse-smart-civic-platform.git
cd civicpulse-smart-civic-platform
```

## 2. Frontend Setup (React + Vite)

1. Install Node modules:
   ```bash
   npm install
   ```

2. Create the environment file:
   Copy `.env.example` to `.env` (or create a new `.env` file) and fill in your keys (see [Environment Variables Guide](./Environment_Variables.md)).

3. Start the development server:
   ```bash
   npm run dev
   ```
   The frontend will run on `http://localhost:5173`.

## 3. Backend Setup (AI Microservice)

1. Navigate to the microservice directory:
   ```bash
   cd ai-microservice
   ```

2. Create a virtual environment:
   ```bash
   # Windows
   python -m venv venv
   venv\Scripts\activate

   # macOS/Linux
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Configure Firebase Admin:
   Place your `firebase_config.json` in the `ai-microservice` directory.

5. Start the FastAPI server:
   ```bash
   python main.py
   ```
   The API will run on `http://localhost:8000`.

## 4. Verification

- Open `http://localhost:5173` in your browser.
- Verify that the YOLO AI service is reachable by sending a test ping to `http://localhost:8000/docs`.
