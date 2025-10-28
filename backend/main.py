# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os

# Routers
from auth.auth import router as auth_router
from auth.upload import router as upload_router

app = FastAPI()

# CORS setup
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Initialize Supabase client
SUPABASE_URL = os.environ.get("SUPABASE_URL")
SUPABASE_SERVICE_ROLE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_ROLE_KEY:
    print("⚠️  Supabase environment variables not set")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print("✅ Supabase client initialized")

# Include routers
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(upload_router, prefix="", tags=["upload"])


@app.get("/")
async def root():
    return {"message": "Backend API is running!"}


# AI Status Endpoint - FIXED VERSION
@app.get("/ai-status/{image_id}")
async def get_ai_status(image_id: str):
    """
    Get AI processing status and results
    """
    try:
        if supabase is None:
            return {
                "status": "error",
                "tags": [],
                "description": "Supabase not configured",
                "colors": [],
            }

        print(f"🔍 Checking AI status for image_id: {image_id}")

        # Check image_metadata table
        result = (
            supabase.table("image_metadata")
            .select("*")
            .eq("image_id", image_id)
            .execute()
        )

        if not result.data:
            return {"status": "not_found", "tags": [], "description": "", "colors": []}

        status_data = result.data[0]
        return {
            "status": status_data.get("ai_processing_status", "unknown"),
            "tags": status_data.get("tags", []),
            "description": status_data.get("description", ""),
            "colors": status_data.get("colors", []),
        }

    except Exception as e:
        print(f"❌ Error in AI status endpoint: {e}")
        return {
            "status": "error",
            "tags": [],
            "description": f"Error: {str(e)}",
            "colors": [],
        }


# Debug endpoints
@app.get("/debug/metadata")
async def debug_metadata():
    """Debug endpoint to see all AI metadata"""
    if supabase is None:
        return {"error": "Supabase not configured"}

    try:
        result = (
            supabase.table("image_metadata")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        return {"metadata": result.data}
    except Exception as e:
        return {"error": str(e)}


@app.get("/debug/images")
async def debug_images():
    """Debug endpoint to see all images"""
    if supabase is None:
        return {"error": "Supabase not configured"}

    try:
        result = (
            supabase.table("images")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )
        return {"images": result.data}
    except Exception as e:
        return {"error": str(e)}


# Test endpoint to verify Supabase connection
@app.get("/test-supabase")
async def test_supabase():
    """Test Supabase connection"""
    if supabase is None:
        return {"status": "error", "message": "Supabase not configured"}

    try:
        # Simple query to test connection
        result = supabase.table("images").select("count", count="exact").execute()
        return {
            "status": "success",
            "message": "Supabase connected",
            "count": result.count,
        }
    except Exception as e:
        return {"status": "error", "message": f"Supabase connection failed: {str(e)}"}
