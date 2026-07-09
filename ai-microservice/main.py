import os
import io
import urllib.request
from fastapi import FastAPI, HTTPException, Depends, Header, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
import csv
import firebase_admin
from firebase_admin import credentials
from firebase_admin import firestore
import uvicorn
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="CivicPulse AI Microservice", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Lazy loading CLIP model to prevent startup hangs
clip_model = None
clip_preprocess = None

CLIP_CLASSES = [
    "a photo of a severe pothole, completely destroyed pavement, or heavily damaged road",
    "a photo of a road with a small pothole, minor surface cracks, or small imperfections",
    "a photo of a massive illegal dump, hazardous waste, or overflowing garbage blocking the street",
    "a photo of a street with some scattered litter, small trash bags, or minor debris",
    "a photo of a broken or malfunctioning traffic light",
    "a photo of an abandoned or derelict car on a street",
    "a photo of a severely flooded street, burst pipe, or deep standing water",
    "a photo of a small water puddle or minor leak on the ground",
    "a photo of a damaged or bent street sign",
    "a photo of graffiti spray painted on a wall",
    "a photo of a fallen tree blocking a road or path",
    "a clean street with no visible problems or damage"
]

CLIP_CLASS_TO_SHORT = {
    "a photo of a severe pothole, completely destroyed pavement, or heavily damaged road": "severe pothole",
    "a photo of a road with a small pothole, minor surface cracks, or small imperfections": "minor road crack",
    "a photo of a massive illegal dump, hazardous waste, or overflowing garbage blocking the street": "severe garbage",
    "a photo of a street with some scattered litter, small trash bags, or minor debris": "minor garbage",
    "a photo of a broken or malfunctioning traffic light": "broken traffic light",
    "a photo of an abandoned or derelict car on a street": "abandoned car",
    "a photo of a severely flooded street, burst pipe, or deep standing water": "severe water leak",
    "a photo of a small water puddle or minor leak on the ground": "minor water leak",
    "a photo of a damaged or bent street sign": "damaged street sign",
    "a photo of graffiti spray painted on a wall": "graffiti",
    "a photo of a fallen tree blocking a road or path": "fallen tree",
    "a clean street with no visible problems or damage": "none"
}

def get_clip():
    global clip_model, clip_preprocess
    if clip_model is None:
        import clip
        import torch
        print("Loading OpenAI CLIP ViT-L/14 model...")
        device = "cuda" if torch.cuda.is_available() else "cpu"
        clip_model, clip_preprocess = clip.load("ViT-L/14", device=device)
        # Pre-tokenize classes
        global text_tokens
        text_tokens = clip.tokenize(CLIP_CLASSES).to(device)
    return clip_model, clip_preprocess

# Mapping our custom classes to priority levels
CLASS_PRIORITY = {
    "severe pothole": "high",
    "minor road crack": "low",
    "severe garbage": "high",
    "minor garbage": "low",
    "broken traffic light": "high",
    "abandoned car": "medium",
    "severe water leak": "high",
    "minor water leak": "low",
    "damaged street sign": "medium",
    "graffiti": "low",
    "fallen tree": "high",
    "none": "none"
}

# Initialize Firebase
firebase_cred_path = os.getenv("FIREBASE_CREDENTIALS_PATH", "firebase_config.json")
try:
    if os.path.exists(firebase_cred_path):
        if not firebase_admin._apps:
            cred = credentials.Certificate(firebase_cred_path)
            firebase_admin.initialize_app(cred)
        db = firestore.client()
        print("Firebase initialized successfully.")
    else:
        db = None
except Exception as e:
    print(f"Warning: Firebase initialization failed: {e}. Ensure firebase_config.json is present.")
    db = None

class PredictionRequest(BaseModel):
    image_url: str
    complaint_id: str

@app.post("/api/predict_priority")
async def predict_priority(request: PredictionRequest):
    try:
        from PIL import Image
        import torch
        
        # Download image
        req = urllib.request.Request(request.image_url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req) as url_resp:
            image_data = url_resp.read()
            
        img = Image.open(io.BytesIO(image_data)).convert('RGB')
        
        # Run Inference
        model_clip, preprocess_clip = get_clip()
        device = "cuda" if torch.cuda.is_available() else "cpu"
        
        image_input = preprocess_clip(img).unsqueeze(0).to(device)
        with torch.no_grad():
            logits_per_image, logits_per_text = model_clip(image_input, text_tokens)
            probs = logits_per_image.softmax(dim=-1).cpu().numpy()[0]
            
        best_idx = probs.argmax()
        best_sentence = CLIP_CLASSES[best_idx]
        best_prob = float(probs[best_idx])
        short_class = CLIP_CLASS_TO_SHORT[best_sentence]
        
        confidence_details = [f"{CLIP_CLASS_TO_SHORT[c].title()} ({p:.2f})" for c, p in zip(CLIP_CLASSES, probs)]
        
        if short_class == "none" or best_prob < 0.1:
            detected_category = "No specific issue detected by AI"
            detected_priority = "medium"
            highest_confidence = 0.0
        else:
            detected_category = short_class.title()
            detected_priority = CLASS_PRIORITY.get(short_class, "medium")
            highest_confidence = round(best_prob, 2)
            
        ai_result = {
            "ai_detected_issue": detected_category,
            "ai_priority": detected_priority.capitalize(),
            "ai_confidence": highest_confidence,
            "ai_details": ", ".join(confidence_details)
        }

        return {"status": "success", "prediction": ai_result}

    except Exception as e:
        print(f"Error processing PredictionRequest: {e}")
        raise HTTPException(status_code=500, detail=str(e))

# ==========================================
# Power BI Export Endpoints
# ==========================================

def get_api_key(x_api_key: str = Header(None)):
    expected_key = os.getenv("POWERBI_API_KEY", "default-dev-key-1234")
    if x_api_key != expected_key:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    return x_api_key

def fetch_and_clean_complaints(from_date: str = None, to_date: str = None, category: str = None, status: str = None):
    if not db:
        raise HTTPException(status_code=500, detail="Database not initialized")
        
    query = db.collection('complaints')
    
    # Firestore simple where clauses
    if category:
        query = query.where('category', '==', category)
    if status:
        query = query.where('status', '==', status)
        
    docs = query.stream()
    cleaned_data = []
    seen_ids = set()
    
    for doc in docs:
        data = doc.to_dict()
        doc_id = doc.id
        
        # 1. Remove duplicates
        if data.get('isDuplicate') is True:
            continue
        if doc_id in seen_ids:
            continue
        seen_ids.add(doc_id)
        
        # 2. Date filtering
        created_at = data.get('createdAt', '')
        if from_date and created_at < from_date:
            continue
        if to_date and created_at > to_date:
            continue
            
        # 3. Geospatial extraction and null checking
        lat = data.get('latitude')
        lng = data.get('longitude')
        if lat is None or lng is None:
            loc = data.get('location', {})
            lat = loc.get('lat')
            lng = loc.get('lng')
            
        if lat is None or lng is None:
            continue # No null latitude/longitude
            
        # 4. Clean schema mapping
        area_name = data.get('areaName') or data.get('location', {}).get('area', 'Unknown')
        severity = data.get('severityScore')
        if severity is None:
            severity = int(data.get('aiSeverity', 0.5) * 100)
            
        cleaned_data.append({
            "id": data.get('customId', doc_id),
            "title": data.get('title', ''),
            "category": data.get('category', ''),
            "latitude": float(lat),
            "longitude": float(lng),
            "areaName": str(area_name),
            "severityScore": int(severity),
            "status": data.get('status', 'submitted'),
            "createdAt": created_at
        })
        
    return cleaned_data

@app.get("/api/export/complaints")
async def export_complaints_json(
    api_key: str = Depends(get_api_key),
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        data = fetch_and_clean_complaints(fromDate, toDate, category, status)
        return data
    except Exception as e:
        print(f"Export Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/export/complaints/csv")
async def export_complaints_csv(
    api_key: str = Depends(get_api_key),
    fromDate: Optional[str] = None,
    toDate: Optional[str] = None,
    category: Optional[str] = None,
    status: Optional[str] = None
):
    try:
        data = fetch_and_clean_complaints(fromDate, toDate, category, status)
        
        def iter_csv():
            output = io.StringIO()
            writer = csv.DictWriter(output, fieldnames=[
                "id", "title", "category", "latitude", "longitude", 
                "areaName", "severityScore", "status", "createdAt"
            ])
            writer.writeheader()
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            
            for row in data:
                writer.writerow(row)
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                
        response = StreamingResponse(iter_csv(), media_type="text/csv")
        response.headers["Content-Disposition"] = "attachment; filename=complaints_export.csv"
        return response
    except Exception as e:
        print(f"CSV Export Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
