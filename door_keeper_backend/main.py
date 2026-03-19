"""
DoorKeeper FastAPI Backend
Main application entry point with API endpoints
"""
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import Dict, List, Any
import uuid
from datetime import datetime
from pathlib import Path

from .rules_engine import RulesEngine
from .compliance import ComplianceCalculator
from .ai_simulation import AISimulation
from .models.schemas import ScanRequest, ScanResponse, Finding

app = FastAPI(
    title="DoorKeeper API",
    description="Security and compliance scanning tool",
    version="1.0.0"
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Resolve paths correctly even when running from backend folder
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_DIR = BASE_DIR / "door_keeper_frontend"

# Serve static files (frontend)
app.mount("/static", StaticFiles(directory=str(FRONTEND_DIR)), name="static")

# In-memory storage for scan reports (use database in production)
scan_reports: Dict[str, Dict[str, Any]] = {}

# Initialize engines
rules_engine = RulesEngine()
compliance_calculator = ComplianceCalculator()
ai_sim = AISimulation()


@app.get("/")
async def root():
    """Serve the frontend application"""
    index_path = FRONTEND_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=500, detail=f"Frontend not found at {index_path}")
    return FileResponse(str(index_path))


@app.post("/scan", response_model=ScanResponse)
async def run_scan(request: ScanRequest):
    """
    Run security/compliance scan on provided configuration
    """
    try:
        # Quick validation to give helpful 400s for bad JSON shapes
        if not isinstance(request.config, dict):
            raise HTTPException(status_code=400, detail="Invalid config: must be a JSON object")

        # Generate unique scan ID
        scan_id = str(uuid.uuid4())

        # Run rules engine to get findings
        findings = rules_engine.run_all_checks(request.config)

        # Calculate compliance score
        compliance_score = compliance_calculator.calculate_score(findings)

        # Generate AI summary (simulated)
        ai_summary = ai_sim.generate_ai_summary(findings)

        # Create scan report
        report = {
            "scan_id": scan_id,
            "timestamp": datetime.now().isoformat(),
            "config": request.config,
            "findings": [f.dict() for f in findings],
            "compliance_score": compliance_score,
            "ai_summary": ai_summary,
            "metadata": request.metadata or {}
        }

        # Store report
        scan_reports[scan_id] = report

        return ScanResponse(
            scan_id=scan_id,
            findings=findings,
            compliance_score=compliance_score,
            timestamp=report["timestamp"],
            ai_summary=ai_summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scan failed: {str(e)}")


@app.get("/report/{scan_id}")
async def get_report(scan_id: str):
    """Retrieve a previously generated scan report"""
    if scan_id not in scan_reports:
        raise HTTPException(status_code=404, detail="Report not found")
    return scan_reports[scan_id]


@app.get("/reports")
async def list_reports():
    """List all available scan reports"""
    summaries = []
    for scan_id, report in scan_reports.items():
        summaries.append({
            "scan_id": scan_id,
            "timestamp": report["timestamp"],
            "compliance_score": report["compliance_score"],
            "findings_count": len(report["findings"])
        })
    return {"reports": summaries}


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "doorkeeper"}


if __name__ == "__main__":
    import uvicorn
    print("Serving frontend from:", FRONTEND_DIR)
    uvicorn.run(app, host="0.0.0.0", port=5000)
