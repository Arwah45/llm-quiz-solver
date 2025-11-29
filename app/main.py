from fastapi import FastAPI, Request, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
import time
from .config import STUDENT_SECRET
from .quiz_solver import solve_quiz_url

app = FastAPI()

@app.post("/")
async def root(request: Request, background_tasks: BackgroundTasks):
    try:
        body = await request.json()
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    email = body.get("email")
    secret = body.get("secret")
    url = body.get("url")

    if not email or not secret or not url:
        raise HTTPException(status_code=400, detail="Missing required fields")

    if secret != STUDENT_SECRET:
        raise HTTPException(status_code=403, detail="Invalid secret")

    deadline = time.time() + 3 * 60  # 3 minutes
    background_tasks.add_task(solve_quiz_url, email, secret, url, deadline)

    return JSONResponse({"status": "accepted"})
