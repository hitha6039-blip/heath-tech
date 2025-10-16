from fastapi import FastAPI, File, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import Optional
import os
import re

app = FastAPI(title="Multi-Modal Medical Data Fusion Diagnostic Assistant")

# CORS - adjust origins to your frontend domain in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For dev only; specify your domain for production
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

def parse_lab_results(lab_results: str):
    """
    Example parser for lab results.
    This looks for glucose level and other numeric data.
    Extend with real parsing logic as needed.
    """
    findings = []
    if not lab_results:
        return ["No lab results provided."]
    
    lab_results_lower = lab_results.lower()
    
    glucose_match = re.search(r'glucose[:\s]*([\d.]+)', lab_results_lower)
    if glucose_match:
        glucose_value = float(glucose_match.group(1))
        if glucose_value > 110:
            findings.append(f"Elevated glucose level detected: {glucose_value} mg/dL.")
        else:
            findings.append(f"Glucose level normal: {glucose_value} mg/dL.")
    else:
        findings.append("Glucose level data not found in lab results.")

    # Add parsing for other lab values here as needed
    
    return findings

@app.post("/diagnose/")
async def diagnose(
    medical_image: Optional[UploadFile] = File(None),
    clinical_text: Optional[str] = Form(None),
    lab_results: Optional[str] = Form(None),
):
    image_info = "No medical image provided."
    if medical_image:
        file_location = os.path.join(UPLOAD_DIR, medical_image.filename)
        with open(file_location, "wb") as f:
            f.write(await medical_image.read())
        image_info = f"Medical image '{medical_image.filename}' received and saved."

    clinical_findings = []
    if clinical_text:
        text_lower = clinical_text.lower()
        if "fever" in text_lower or "cough" in text_lower or "infection" in text_lower:
            clinical_findings.append("Clinical symptoms suggest possible infection.")
        else:
            clinical_findings.append("No significant clinical symptoms detected.")
    else:
        clinical_findings.append("No clinical text provided.")

    lab_findings = parse_lab_results(lab_results)

    # Combine all diagnostic info
    diagnostic_summary = "\n".join([image_info] + clinical_findings + lab_findings)

    return JSONResponse(content={"diagnosis": diagnostic_summary})
