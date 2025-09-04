from google_sheets import write_result_to_sheet
import subprocess
import tempfile
from fastapi import FastAPI, UploadFile, File, WebSocket, WebSocketDisconnect, Depends
import json
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import List, Optional
import uuid
from sqlalchemy.orm import Session
from db import SessionLocal, InterviewDB, ResumeDB, engine



import os
UPLOAD_DIR = os.path.join(os.path.dirname(__file__), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

app = FastAPI()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Модели
class ResumeInfo(BaseModel):
    filename: str
    url: str

class InterviewCreate(BaseModel):
    position: str
    job_description: str
    resumes: List[ResumeInfo]

class Interview(BaseModel):
    id: str
    position: str
    job_description: str
    resumes: List[ResumeInfo]
    status: str
    results_url: Optional[str]



@app.post("/api/hr/interviews", response_model=Interview)
def create_interview(data: InterviewCreate, db: Session = Depends(get_db)):
    interview_id = str(uuid.uuid4())
    interview_db = InterviewDB(
        id=interview_id,
        position=data.position,
        job_description=data.job_description,
        status="created",
        results_url=None
    )
    db.add(interview_db)
    db.commit()
    db.refresh(interview_db)
    resumes_out = []
    for resume in data.resumes:
        resume_db = ResumeDB(
            filename=resume.filename,
            url=resume.url,
            interview_id=interview_id
        )
        db.add(resume_db)
        resumes_out.append(resume)
    db.commit()
    return Interview(
        id=interview_db.id,
        position=interview_db.position,
        job_description=interview_db.job_description,
        resumes=resumes_out,
        status=interview_db.status,
        results_url=interview_db.results_url
    )

@app.get("/api/hr/interviews", response_model=List[Interview])
def list_interviews(db: Session = Depends(get_db)):
    interviews = db.query(InterviewDB).all()
    result = []
    for interview in interviews:
        resumes = db.query(ResumeDB).filter(ResumeDB.interview_id == interview.id).all()
        resumes_out = [ResumeInfo(filename=r.filename, url=r.url) for r in resumes]
        result.append(Interview(
            id=interview.id,
            position=interview.position,
            job_description=interview.job_description,
            resumes=resumes_out,
            status=interview.status,
            results_url=interview.results_url
        ))
    return result

@app.get("/api/hr/results/{interview_id}")
def get_results(interview_id: str, db: Session = Depends(get_db)):
    interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
    if not interview or not interview.results_url:
        return {"error": "Результаты не найдены"}
    return {"results_url": interview.results_url}

@app.get("/api/hr/requirements/{interview_id}")
def get_requirements(interview_id: str, db: Session = Depends(get_db)):
    interview = db.query(InterviewDB).filter(InterviewDB.id == interview_id).first()
    if not interview:
        return {"error": "Собеседование не найдено"}
    resumes = db.query(ResumeDB).filter(ResumeDB.interview_id == interview_id).all()
    resumes_out = [ResumeInfo(filename=r.filename, url=r.url) for r in resumes]
    return {"job_description": interview.job_description, "resumes": resumes_out}

# WebSocket для интервью
@app.websocket("/ws/interview/{session_id}")
async def interview_ws(websocket: WebSocket, session_id: str):
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
# Заглушки для хранения


# Множественная загрузка файлов
@app.post("/api/hr/upload-multi")
async def upload_files(files: List[UploadFile] = File(...)):
    result = []
    for file in files:
        file_location = os.path.join(UPLOAD_DIR, file.filename)
        with open(file_location, "wb") as f:
            content = await file.read()
            f.write(content)
        result.append({
            "filename": file.filename,
            "url": f"/api/hr/file/{file.filename}"
        })
    return {"files": result}

@app.get("/api/hr/file/{filename}")
def get_uploaded_file(filename: str):
    file_location = os.path.join(UPLOAD_DIR, filename)
    if not os.path.exists(file_location):
        return {"error": "Файл не найден"}
    return FileResponse(file_location, media_type="application/octet-stream", filename=filename)
# Заглушки для хранения

@app.post("/api/hr/score")
async def score_candidate(data: dict):
    # Сохраняем входные данные во временный файл
    with tempfile.NamedTemporaryFile(mode="w", delete=False, suffix=".json") as f:
        json.dump(data, f)
        input_path = f.name
    output_path = input_path.replace(".json", "_score.json")
    # Запускаем скоринг-скрипт
    result = subprocess.run([
        "python", "../../ds3/score_candidate.py", input_path, output_path
    ], capture_output=True, text=True)
    if result.returncode != 0:
        return {"error": "Ошибка скоринга", "details": result.stderr}
    # Читаем результат
    with open(output_path, "r") as f:
        score_data = json.load(f)
    # Записываем результат в Google Sheets
    try:
        write_result_to_sheet(score_data)
    except Exception as e:
        print(f"Ошибка записи в Google Sheets: {e}")
    return score_data
