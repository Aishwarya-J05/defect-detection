from fastapi import FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import shutil
import os
import base64
from detect import detect_defects

app = FastAPI(title="Industrial Defect Detection API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"message": "Defect Detection API is running ✅"}

@app.post("/analyze")
async def analyze(file: UploadFile = File(...)):
    # Save uploaded image temporarily
    temp_path = f"temp_{file.filename}"
    with open(temp_path, "wb") as f:
        shutil.copyfileobj(file.file, f)

    # Run detection
    result = detect_defects(temp_path)
    os.remove(temp_path)

    # Convert annotated image to base64 to send in response
    with open(result["annotated_image"], "rb") as f:
        img_base64 = base64.b64encode(f.read()).decode()

    os.remove(result["annotated_image"])

    return JSONResponse({
        "detections": result["detections"],
        "annotated_image": img_base64
    })