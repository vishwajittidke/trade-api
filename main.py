from dotenv import load_dotenv
load_dotenv()

import logging
from datetime import datetime, timezone

from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel, Field

from config import ALLOWED_SECTORS
from utils.auth import create_token, verify_token
from utils.rate_limiter import is_allowed
from utils.session import SessionManager
from utils.validator import validate_sector
from pipeline import run_pipeline

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
log = logging.getLogger("trade_api")

sessions = SessionManager()
security = HTTPBearer()

# data models for the api
class TokenRequest(BaseModel):
    username: str = Field(..., min_length=1, max_length=50, example="analyst_1")

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    expires_in: int = 3600
    session_id: str

app = FastAPI(
    title="Trade Opportunities API India",
    description="Analyze Indian market sectors and generate AI trade reports. Uses real-time search + Gemini AI.",
    version="1.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], allow_credentials=True,
    allow_methods=["*"], allow_headers=["*"],
)

@app.get("/health", tags=["system"])
async def health():
    return {"status": "ok", "timestamp": datetime.now(timezone.utc).isoformat()}

@app.post("/auth/token", response_model=TokenResponse, tags=["auth"])
async def login(body: TokenRequest):
    """Get a JWT token for the /analyze endpoint."""
    token = create_token(body.username)
    session_id = sessions.create_session(body.username)
    log.info(f"Issuing token for: {body.username}")
    return TokenResponse(access_token=token, session_id=session_id)

@app.get("/analyze/{sector}", tags=["analysis"])
async def analyze(sector: str, creds: HTTPAuthorizationCredentials = Depends(security)):
    """Generates a full markdown market analysis for the chosen sector."""
    user_id = verify_token(creds.credentials)
    if not user_id:
        raise HTTPException(401, "Token is invalid or expired")

    if not is_allowed(user_id):
        raise HTTPException(429, "Woah, too fast. Rate limit exceeded.")

    # track this bit in the session
    sid = sessions.get_or_create_session(user_id)
    sessions.track_request(sid, f"/analyze/{sector}")

    try:
        sector = validate_sector(sector)
        log.info(f"Running report for {sector} (user: {user_id})")
        
        md_report = await run_pipeline(sector)
        return {
            "sector": sector,
            "markdown": md_report,
            "session_id": sid,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }

    except ValueError as e:
        raise HTTPException(400, str(e))
    except Exception as e:
        log.error(f"Error in pipeline: {e}", exc_info=True)
        raise HTTPException(500, "Something went wrong in the analyzer pipeline.")

@app.get("/sectors", tags=["reference"])
async def get_sectors():
    """List out all the sectors we currently support."""
    return {"sectors": sorted(ALLOWED_SECTORS)}