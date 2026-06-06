import os
import json
import pandas as pd
from io import StringIO
from file_classifier import classify_file, quick_classify_csv

UPLOAD_DIR = "uploaded_files"
CSV_DIR = os.path.join(UPLOAD_DIR, "csv")
TEXT_DIR = os.path.join(UPLOAD_DIR, "text")
META_FILE = os.path.join(UPLOAD_DIR, "file_metadata.json")

os.makedirs(CSV_DIR, exist_ok=True)
os.makedirs(TEXT_DIR, exist_ok=True)


def load_metadata():
    if not os.path.exists(META_FILE):
        return []

    with open(META_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def save_metadata(metadata):
    with open(META_FILE, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2)


def save_uploaded_file(filename, content_bytes):
    if filename.endswith(".xlsx"):
        import pandas as pd
        from io import BytesIO
        df = pd.read_excel(BytesIO(content_bytes))
        columns = set(df.columns)
        if {"EmployeeID", "Employee", "Team"}.issubset(columns):
            file_type = "employee_master"
        elif {"EmployeeID", "PerformanceRating"}.issubset(columns):
            file_type = "performance"
        elif {"EmployeeID", "WeeklyHours"}.issubset(columns):
            file_type = "workload"
        elif {"EmployeeID", "Skill"}.issubset(columns):
            file_type = "skills"
        elif {"OwnerID", "Owner", "DependentID", "Dependent"}.issubset(columns):
            file_type = "dependencies"
        elif {"ProjectID", "Project", "Team"}.issubset(columns):
            file_type = "projects"
        else:
            file_type = "unknown"
        path = os.path.join(CSV_DIR, filename)
        description = f"Excel file detected as {file_type}"
        with open(path, "wb") as f:
            f.write(content_bytes)
    else:
        content = content_bytes.decode("utf-8")
        if filename.endswith(".csv"):
            file_type = quick_classify_csv(content)
            if file_type == "unknown":
                classification = classify_file(filename, content)
                file_type = classification["file_type"]
                description = classification["description"]
            else:
                description = f"Detected as {file_type} using CSV columns"
            path = os.path.join(CSV_DIR, filename)
        elif filename.endswith(".txt"):
            classification = classify_file(filename, content)
            file_type = classification["file_type"]
            description = classification["description"]
            if file_type == "unknown":
                file_type = "review_notes"
            path = os.path.join(TEXT_DIR, filename)
        elif filename.endswith(".docx"):
            file_type = "document"
            description = "Word document"
            path = os.path.join(TEXT_DIR, filename)
        else:
            raise ValueError("Only CSV, TXT, XLSX, and DOCX files supported")
        with open(path, "wb") as f:
            f.write(content_bytes)

    metadata = load_metadata()

    metadata.append({
        "filename": filename,
        "path": path,
        "file_type": file_type,
        "description": description
    })

    save_metadata(metadata)

    return {
        "filename": filename,
        "path": path,
        "file_type": file_type,
        "description": description
    }


def get_employee_structured_data(employee_id):
    result = {}

    for file_name in os.listdir(CSV_DIR):
        path = os.path.join(CSV_DIR, file_name)
        try:
            if file_name.endswith(".csv"):
                df = pd.read_csv(path)
            elif file_name.endswith(".xlsx"):
                df = pd.read_excel(path)
            else:
                continue
        except Exception:
            continue

        if "EmployeeID" not in df.columns:
            continue

        df["EmployeeID"] = df["EmployeeID"].astype(str).str.strip()
        employee_id = str(employee_id).strip()

        rows = df[df["EmployeeID"] == employee_id]

        if not rows.empty:
            result[file_name] = rows.to_dict(orient="records")

    return result
def get_employee_text_notes(employee_id):
    metadata = load_metadata()
    notes = []

    for item in metadata:
        if not item["path"].endswith(".txt"):
            continue

        with open(item["path"], "r", encoding="utf-8") as f:
            content = f.read()

        if str(employee_id) in content:
            notes.append({
                "filename": item["filename"],
                "file_type": item["file_type"],
                "description": item["description"],
                "content": content
            })

    return notes