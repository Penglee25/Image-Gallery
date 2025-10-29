# main.py
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from supabase import create_client
import os

# Routers
from auth.auth import router as auth_router
from auth.upload import router as upload_router
from auth.gallery import router as gallery_router


app = FastAPI()

# CORS setup
# origins = [
#     "http://localhost:5173",
#     "http://127.0.0.1:5173",
# ]

origins = [
    "https://image-gallery-frontend-t0lb.onrender.com", 
    "http://localhost:5173",
    "http://localhost:4173",
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
    print("Supabase environment variables not set")
    supabase = None
else:
    supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_ROLE_KEY)
    print("Supabase client initialized")

# Include routers
app.include_router(auth_router, prefix="", tags=["auth"])
app.include_router(upload_router, prefix="", tags=["upload"])
app.include_router(gallery_router, prefix="", tags=["gallery"])


@app.get("/")
async def root():
    return {"message": "Backend API is running!"}


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
