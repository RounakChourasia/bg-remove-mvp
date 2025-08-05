# app/main.py
import io
import uuid
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import StreamingResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from rembg import remove
from starlette.status import HTTP_400_BAD_REQUEST

# ---------------------------------------------------------
# FastAPI app + CORS (open for now – change later for prod)
# ---------------------------------------------------------
app = FastAPI(
    title="Free Background Remover",
    description="Upload an image and receive the same image with the background removed.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],          # 👉 Change to your domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ---------------------------------------------------------
# Helper: size & MIME validation (2 MiB limit)
# ---------------------------------------------------------
MAX_SIZE = 2 * 1024 * 1024   # 2 MiB

def _validate_upload(file: UploadFile):
    # Only PNG or JPEG allowed
    if file.content_type not in {"image/png", "image/jpeg", "image/jpg"}:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="Only PNG and JPEG files are supported."
        )
    # Check size, read only up to limit+1 bytes
    content = file.file.read(MAX_SIZE + 1)
    if len(content) > MAX_SIZE:
        raise HTTPException(
            status_code=HTTP_400_BAD_REQUEST,
            detail="File too large – limit is 2 MiB."
        )
    file.file.seek(0)
    return True

# ---------------------------------------------------------
# API endpoint – POST /remove
# ---------------------------------------------------------
@app.post("/remove")
async def remove_background(file: UploadFile = File(...)):
    """
    Accept a PNG/JPEG, run `rembg` model, and stream back a PNG
    with a transparent background.
    """
    _validate_upload(file)
    raw_bytes = await file.read()
    try:
        result_bytes = remove(raw_bytes)      # 👈 <‑‑ the magic happens here
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail=f"Background removal failed: {exc}"
        )
    # Stream PNG straight to the client (no temp files)
    return StreamingResponse(
        io.BytesIO(result_bytes),
        media_type="image/png",
        headers={"Content‑Disposition": f'inline; filename="{uuid.uuid4()}.png"'}
    )

# ---------------------------------------------------------
# Simple health‑check
# ---------------------------------------------------------
@app.get("/health")
async def health():
    return JSONResponse(content={"status": "ok"})
