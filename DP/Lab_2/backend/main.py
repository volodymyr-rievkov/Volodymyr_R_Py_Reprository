from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes.lab_1 import router as lab1_router
from app.routes.lab_2 import router as lab2_router
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
app.include_router(lab2_router, prefix="/lab2")