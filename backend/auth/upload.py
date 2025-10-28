# auth/upload.py
import os
from fastapi import APIRouter, UploadFile, File, Header, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from supabase import create_client
from uuid import uuid4
from PIL import Image
from io import BytesIO

# Import AI analysis
from ai_utils_gemini import analyze_image_ai

router = APIRouter()

# ----------------------------
# Environment variables
# ----------------------------
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
SUPABASE_BUCKET = os.environ.get("SUPABASE_BUCKET", "images")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    raise Exception("Supabase URL and Service Role Key must be set in env")

# Initialize Supabase client
supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)


# ----------------------------
# Helpers
# ----------------------------
def create_thumbnail(file_bytes):
    """Create a 300x300 thumbnail from image bytes"""
    img = Image.open(BytesIO(file_bytes))
    img.thumbnail((300, 300))
    buffer = BytesIO()
    img.save(buffer, format="JPEG")
    buffer.seek(0)
    return buffer.read()


def process_ai_metadata(user_id: str, image_id: str, file_bytes: bytes):
    """Background task to analyze image with AI and store metadata"""
    try:
        tags, description, colors = analyze_image_ai(file_bytes)

        # Ensure we have valid arrays for PostgreSQL
        tags_array = tags if isinstance(tags, list) else []
        colors_array = colors if isinstance(colors, list) else []

        # Convert empty strings to None for description
        description_value = (
            description if description and description != "Analysis failed" else None
        )

        supabase.table("image_metadata").insert(
            {
                "user_id": user_id,
                "image_id": image_id,
                "description": description_value,
                "tags": tags_array,
                "colors": colors_array,
                "ai_processing_status": "done",
            }
        ).execute()
        print(f"✅ AI metadata saved for image_id={image_id}")

    except Exception as e:
        print(f"❌ AI processing failed for image_id={image_id}: {e}")
        # Insert with empty arrays
        supabase.table("image_metadata").insert(
            {
                "user_id": user_id,
                "image_id": image_id,
                "description": None,
                "tags": [],
                "colors": [],
                "ai_processing_status": "failed",
            }
        ).execute()


# ----------------------------
# Upload Endpoint
# ----------------------------
@router.post("/upload")
async def upload_files(
    files: list[UploadFile] = File(...),
    x_user_id: str = Header(None),
    background_tasks: BackgroundTasks = None,
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

            # ----------------------------
            # Upload original + thumbnail
            # ----------------------------
            try:
                supabase.storage.from_(SUPABASE_BUCKET).upload(
                    f"{x_user_id}/{filename}", content, {"cacheControl": "3600"}
                )

                supabase.storage.from_(SUPABASE_BUCKET).upload(
                    f"{x_user_id}/{thumbnail_filename}",
                    thumbnail_bytes,
                    {"cacheControl": "3600"},
                )
            except Exception as e:
                uploaded_results.append(
                    {
                        "filename": file.filename,
                        "ai_processing_status": "failed",
                        "error": str(e),
                    }
                )
                continue

            # ----------------------------
            # Insert into images table
            # ----------------------------
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

            # Ensure we got data back
            if not db_res or not db_res.data:
                uploaded_results.append(
                    {
                        "filename": file.filename,
                        "ai_processing_status": "failed",
                        "error": "Failed to insert image record",
                    }
                )
                continue

            image_id = db_res.data[0]["id"]

            # ----------------------------
            # Schedule AI processing in background
            # ----------------------------
            if background_tasks:
                background_tasks.add_task(
                    process_ai_metadata, x_user_id, image_id, content
                )

            uploaded_results.append(
                {
                    "filename": file.filename,
                    "original_path": f"{x_user_id}/{filename}",
                    "thumbnail_path": f"{x_user_id}/{thumbnail_filename}",
                    "image_id": image_id,
                    "ai_processing_status": "pending",
                }
            )

        except Exception as e:
            uploaded_results.append(
                {
                    "filename": file.filename,
                    "ai_processing_status": "failed",
                    "error": str(e),
                }
            )

    return JSONResponse({"uploaded": uploaded_results})
