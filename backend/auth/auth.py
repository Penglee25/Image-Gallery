# auth.py
from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from supabase import create_client, Client
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

# Initialize Supabase client
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# Pydantic models for request validation
class SignupRequest(BaseModel):
    email: EmailStr
    password: str


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


# SIGNUP FUNCTION
def signup_user(data: SignupRequest):
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


# LOGIN FUNCTION
def login_user(data: LoginRequest):
    try:
        result = supabase.auth.sign_in_with_password(
            {"email": data.email, "password": data.password}
        )

        if not result or not result.user:
            raise HTTPException(status_code=401, detail="Invalid credentials")

        return {
            "message": "Login successful",
            "access_token": result.session.access_token,
        }

    except Exception as e:
        print("Login error:", e)
        raise HTTPException(
            status_code=500, detail="Internal server error during login"
        )
