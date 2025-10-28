# auth.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise Exception("Supabase URL or Service Role Key not set")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Pydantic models
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# Router
router = APIRouter()


# SIGNUP
@router.post("/signup")
def signup_user_endpoint(data: SignupRequest):
    try:
        response = supabase.auth.sign_up(
            {"email": data.email, "password": data.password}
        )
        if not response or not response.user:
            raise HTTPException(status_code=400, detail="Signup failed. Try again.")

        return {"message": f"User {data.email} registered successfully!"}

    except Exception as e:
        print("Signup error:", e)
        raise HTTPException(
            status_code=500, detail="Internal server error during signup"
        )


# LOGIN
@router.post("/login")
def login_user_endpoint(data: LoginRequest):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )

        if not result or not result.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        user_id = result.user.id  # get the Supabase user ID

        return {
            "message": "Login successful",
            "access_token": result.session.access_token,
            "user_id": user_id
        }

    except Exception as e:
        print("Login error:", e)
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )


# LOGOUT (optional)
@router.post("/logout")
def logout_user_endpoint():
    # For stateless token-based auth, logout can be handled client-side by deleting tokens
    return {"message": "Logged out successfully"}
