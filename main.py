import os
import time
import uuid

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.responses import Response

# >>> SET THIS to your exact logged-in email (or set the EMAIL env var on the host) <<<
EMAIL = os.environ.get("EMAIL", "25f2004578@ds.study.iitm.ac.in")
ALLOWED_ORIGIN = "https://dash-q6sh4h.example.com"

app = FastAPI()


@app.middleware("http")
async def common_middleware(request: Request, call_next):
    start = time.perf_counter()
    origin = request.headers.get("origin")
    allowed = origin == ALLOWED_ORIGIN

    # Preflight handling: only the allowed origin gets ACAO
    if request.method == "OPTIONS":
        if allowed:
            response = Response(status_code=200)
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN
            response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            req_headers = request.headers.get("access-control-request-headers")
            response.headers["Access-Control-Allow-Headers"] = req_headers or "*"
            response.headers["Access-Control-Max-Age"] = "600"
        else:
            response = Response(status_code=403, content="Disallowed CORS origin")
    else:
        response = await call_next(request)
        if allowed:
            response.headers["Access-Control-Allow-Origin"] = ALLOWED_ORIGIN

    response.headers["Vary"] = "Origin"
    response.headers["X-Request-ID"] = str(uuid.uuid4())
    response.headers["X-Process-Time"] = f"{time.perf_counter() - start:.6f}"
    return response


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/stats")
def stats(values: str = Query(...)):
    try:
        nums = [int(v.strip()) for v in values.split(",") if v.strip() != ""]
    except ValueError:
        raise HTTPException(status_code=400, detail="values must be comma-separated integers")
    if not nums:
        raise HTTPException(status_code=400, detail="no values provided")
    total = sum(nums)
    return {
        "email": EMAIL,
        "count": len(nums),
        "sum": total,
        "min": min(nums),
        "max": max(nums),
        "mean": total / len(nums),
    }
