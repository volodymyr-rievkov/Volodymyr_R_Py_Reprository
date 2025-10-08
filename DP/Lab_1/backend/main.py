from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import router as lab1_router
from config import ALLOWED_ORIGINS

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=ALLOWED_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(lab1_router, prefix="/lab1")