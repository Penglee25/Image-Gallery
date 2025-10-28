# auth/upload.py
import os
from fastapi import APIRouter, UploadFile, File, Header, HTTPException
from fastapi.responses import JSONResponse
from supabase import create_client
from uuid import uuid4
from PIL import Image
from io import BytesIO
from pydantic import BaseModel

router = APIRouter()

# ----------------------------
# Environment variables
# ----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "images")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise Exception(
        "Supabase URL and Service Role Key must be set in environment variables"
    )

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ----------------------------
# Helpers
# ----------------------------
def create_thumbnail(file_bytes: bytes, size: int = 300) -> bytes:
    """Create a thumbnail from image bytes"""
    img = Image.open(BytesIO(file_bytes))
    img.thumbnail((size, size))
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.read()


# ----------------------------
# Upload Endpoint
# ----------------------------
@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    x_user_id: str = Header(None),
):
    if not x_user_id:
        raise HTTPException(status_code=401, detail="Missing user_id header")

    uploaded_results = []

    for file in files:
        try:
            content = await file.read()
            filename = f"{uuid4().hex}_{file.filename}"
            thumbnail_bytes = create_thumbnail(content)
            thumbnail_filename = f"thumb_{filename}"

            # Upload original + thumbnail to Supabase
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                f"{x_user_id}/{filename}", content, {"cacheControl": "3600"}
            )
            supabase.storage.from_(SUPABASE_BUCKET).upload(
                f"{x_user_id}/{thumbnail_filename}",
                thumbnail_bytes,
                {"cacheControl": "3600"},
            )

            # Insert into images table
            db_res = (
                supabase.table("images")
                .insert(
                    {
                        "user_id": x_user_id,
                        "filename": file.filename,
                        "original_path": f"{x_user_id}/{filename}",
                        "thumbnail_path": f"{x_user_id}/{thumbnail_filename}",
                    }
                )
                .execute()
            )

            image_id = db_res.data[0]["id"] if db_res.data else None

            uploaded_results.append(
                {
                    "filename": file.filename,
                    "original_path": f"{x_user_id}/{filename}",
                    "thumbnail_path": f"{x_user_id}/{thumbnail_filename}",
                    "image_id": image_id,
                }
            )

        except Exception as e:
            uploaded_results.append(
                {
                    "filename": file.filename,
                    "error": str(e),
                }
            )

    return JSONResponse({"uploaded": uploaded_results})


# ----------------------------
# AI Metadata Endpoint
# ----------------------------
class AIMetadata(BaseModel):
    image_id: int
    user_id: str
    description: str | None = None
    tags: list[str] = []
    colors: list[str] = []
    ai_processing_status: str = "done"


@router.post("/ai-metadata")
async def insert_ai_metadata(data: AIMetadata):
    try:
        
        def rgb_to_hex(rgb_str):
            # rgb_str = "rgb(41,184,103)"
            nums = [int(n) for n in rgb_str.strip("rgb()").split(",")]
            return "#{:02X}{:02X}{:02X}".format(*nums)

        # Limit colors to top 3 dominant colors
        colors_array = [rgb_to_hex(c)[:7] for c in data.colors[:3]]

        res = (
            supabase.table("image_metadata")
            .insert(
                {
                    "image_id": data.image_id,
                    "user_id": data.user_id,
                    "description": data.description,
                    "tags": data.tags,
                    "colors": colors_array,  # <-- only top 3
                    "ai_processing_status": data.ai_processing_status,
                }
            )
            .execute()
        )

        if not res or not res.data:
            raise HTTPException(status_code=500, detail="Failed to insert AI metadata")

        return JSONResponse({"status": "success", "data": res.data})

    except Exception as e:
        return JSONResponse({"status": "error", "message": str(e)})
