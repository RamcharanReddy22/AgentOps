from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel
import pypdf
import io
import os
from agents.researcher import run_researcher
from agents.analyst import run_analyst
from pipeline import run_pipeline
from rag.vector_store import add_documents

app = FastAPI(title="AgentOps - Market Research Autopilot")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("/home/ubuntu/agentops/charts", exist_ok=True)
os.makedirs("/home/ubuntu/agentops/static", exist_ok=True)
app.mount("/charts", StaticFiles(directory="/home/ubuntu/agentops/charts"), name="charts")
app.mount("/static", StaticFiles(directory="/home/ubuntu/agentops/static"), name="static")

class AnalyzeRequest(BaseModel):
    query: str

@app.get("/")
def root():
    return FileResponse("/home/ubuntu/agentops/static/index.html")

@app.post("/analyze")
def analyze(req: AnalyzeRequest):
    result = run_researcher(req.query)
    return {"query": req.query, "report": result}

@app.post("/analyze/financial")
def analyze_financial(req: AnalyzeRequest):
    result = run_analyst(req.query)
    return {"query": req.query, "report": result}

@app.post("/analyze/full")
def analyze_full(req: AnalyzeRequest):
    result = run_pipeline(req.query)
    return result

@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    contents = await file.read()
    reader = pypdf.PdfReader(io.BytesIO(contents))
    texts = [page.extract_text() for page in reader.pages if page.extract_text()]
    ids = [f"{file.filename}_page_{i}" for i in range(len(texts))]
    add_documents(texts, ids)
    return {"status": "ok", "pages_uploaded": len(texts), "filename": file.filename}
