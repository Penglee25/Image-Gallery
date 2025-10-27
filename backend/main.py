# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth.auth import SignupRequest, LoginRequest, signup_user, login_user
from fastapi.responses import JSONResponse

app = FastAPI()

# ✅ CORS setup — must come BEFORE route definitions
origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # or ["*"] for all
    allow_credentials=True,
    allow_methods=["*"],  # must include OPTIONS
    allow_headers=["*"],  # must include Content-Type, Authorization
)


@app.get("/")
async def root():
    return {"message": "Backend API is running!"}


@app.post("/signup")
async def signup(data: SignupRequest):
    return signup_user(data)


@app.post("/login")
async def login(data: LoginRequest):
    return login_user(data)


@app.post("/logout")
async def logout():
    response = JSONResponse(content={"message": "Logged out successfully"})
    response.delete_cookie("sb-access-token")
    response.delete_cookie("sb-refresh-token")
    return response
