from fastapi import FastAPI, UploadFile, File
import os
import pandas as pd
from io import StringIO

from storage import (
    CSV_DIR,
    TEXT_DIR,
    get_employee_structured_data,
    get_employee_text_notes,
    load_metadata
)

from analyzer import analyze_employee_context

app = FastAPI()

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


@app.get("/")
def home():
    return {"message": "TruPulse AI is running"}


@app.post("/upload-file")
async def upload_file(file: UploadFile = File(...)):
    try:
        content = await file.read()
        filename = file.filename.lower()

        if filename.endswith(".csv"):
            csv_text = content.decode("utf-8")
            df = pd.read_csv(StringIO(csv_text))

            file_path = os.path.join(CSV_DIR, file.filename)

            with open(file_path, "wb") as f:
                f.write(content)

            return {
                "message": "CSV uploaded successfully",
                "filename": file.filename,
                "stored_path": file_path,
                "rows": len(df),
                "columns": list(df.columns)
            }

        elif filename.endswith(".txt"):
            file_path = os.path.join(TEXT_DIR, file.filename)

            with open(file_path, "wb") as f:
                f.write(content)

            return {
                "message": "Text file uploaded successfully",
                "filename": file.filename,
                "stored_path": file_path
            }

        else:
            return {"error": "Only CSV and TXT files are supported"}

    except Exception as e:
        return {"error": str(e)}


@app.get("/files")
def get_files():
    return {"files": load_metadata()}


@app.get("/employee-data/{employee_id}")
def employee_data(employee_id: str):
    return {
        "employee_id": employee_id,
        "structured_data": get_employee_structured_data(employee_id),
        "text_notes": get_employee_text_notes(employee_id)
    }


@app.post("/analyze-employee/{employee_id}")
def analyze_employee(employee_id: str):
    structured_data = get_employee_structured_data(employee_id)
    text_notes = get_employee_text_notes(employee_id)

    if not structured_data and not text_notes:
        return {
            "employee_id": employee_id,
            "error": "No data found for this employee ID"
        }

    analysis = analyze_employee_context(
        employee_id,
        structured_data,
        text_notes
    )

    return {
        "employee_id": employee_id,
        "structured_data": structured_data,
        "text_notes": text_notes,
        "analysis": analysis
    }