from fastapi import FastAPI, UploadFile, File
from pydantic import BaseModel
import pandas as pd
from simulator import simulate_employee_loss
from ai_analyser import analyze_risk

app = FastAPI()

class SimulationRequest(BaseModel):
    employee: str



@app.get("/")
def home():
    return {"message": "TruPulse AI"}

@app.post("/upload-csv")
async def upload_csv(file: UploadFile = File(...)):

    contents = await file.read()

    with open("employees.csv", "wb") as f:
        f.write(contents)

    return {"message": "CSV uploaded successfully"}

@app.post("/simulate")
def simulate(request: SimulationRequest):

    result = simulate_employee_loss(
        request.employee
    )

    return result
@app.post("/analyze")
def analyze(request: SimulationRequest):

    simulation_result = simulate_employee_loss(
        request.employee
    )

    analysis = analyze_risk(
        simulation_result
    )

    return {
        "simulation": simulation_result,
        "analysis": analysis
    }