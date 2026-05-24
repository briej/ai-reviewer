from pathlib import Path
from typing import Optional, List
from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
import uvicorn

from src.analyzer import fast_analyze
from src.scanner import scan_files, read_file

app = FastAPI(title="ai-reviewer API", version="1.3.1")

# Static files and templates
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# In-memory storage for scan results
scan_results = {}


class ScanRequest(BaseModel):
    """Request model for scan endpoint."""
    path: str
    mode: str = "fast"
    provider: Optional[str] = "ollama"
    model: Optional[str] = "llama3.1:8b"


class Issue(BaseModel):
    """Issue model."""
    severity: str
    type: str
    location: str
    message: str


@app.get("/", response_class=HTMLResponse)
async def home(request):
    """Home page."""
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/api/scan")
async def scan_project(
    path: str = Form(...),
    mode: str = Form("fast"),
    provider: Optional[str] = Form("ollama"),
    model: Optional[str] = Form("llama3.1:8b"),
):
    """Scan a project for vulnerabilities."""
    project_path = Path(path)
    
    if not project_path.exists():
        return JSONResponse(
            status_code=404,
            content={"error": f"Path not found: {path}"}
        )
    
    try:
        # Scan files
        files = scan_files(project_path)
        all_issues: List[Issue] = []
        
        # Analyze each file
        for file_path in files:
            content = read_file(file_path)
            if mode == "fast":
                issues = fast_analyze(file_path, content)
            else:
                # TODO: Add AI mode
                issues = fast_analyze(file_path, content)
            
            for issue in issues:
                all_issues.append(Issue(**issue))
        
        # Store results
        scan_id = str(len(scan_results) + 1)
        scan_results[scan_id] = {
            "path": str(path),
            "mode": mode,
            "issues": [i.dict() for i in all_issues],
            "summary": {
                "critical": len([i for i in all_issues if i.severity == "critical"]),
                "warning": len([i for i in all_issues if i.severity == "warning"]),
                "info": len([i for i in all_issues if i.severity == "info"]),
            }
        }
        
        return JSONResponse(content={
            "scan_id": scan_id,
            "summary": scan_results[scan_id]["summary"],
            "total_issues": len(all_issues),
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/results/{scan_id}")
async def get_results(scan_id: str):
    """Get scan results by ID."""
    if scan_id not in scan_results:
        return JSONResponse(
            status_code=404,
            content={"error": "Scan not found"}
        )
    
    return JSONResponse(content=scan_results[scan_id])


@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    """Upload a single file for analysis."""
    try:
        # Save uploaded file
        temp_path = Path("temp") / file.filename
        temp_path.parent.mkdir(exist_ok=True)
        
        content = await file.read()
        temp_path.write_bytes(content)
        
        # Analyze
        issues = fast_analyze(temp_path, content.decode("utf-8"))
        
        # Clean up
        temp_path.unlink()
        
        return JSONResponse(content={
            "filename": file.filename,
            "issues": issues,
            "count": len(issues)
        })
    
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/api/providers")
async def get_providers():
    """Get available AI providers."""
    return JSONResponse(content={
        "providers": [
            {"name": "ollama", "type": "local", "default_model": "llama3.1:8b"},
            {"name": "deepseek", "type": "cloud", "default_model": "deepseek-coder"},
            {"name": "openrouter", "type": "cloud", "default_model": "claude-3"},
            {"name": "groq", "type": "cloud", "default_model": "llama3-70b"},
        ]
    })


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return JSONResponse(content={"status": "ok", "version": "1.3.1"})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
