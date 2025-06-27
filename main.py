
import os
from pathlib import Path

from fastapi.middleware.cors import CORSMiddleware
from fastapi import FastAPI, HTTPException,Depends
from dotenv import load_dotenv
from fastapi.responses import JSONResponse
from core.db import engine,Base
from sqlalchemy.orm import Session
from sqlalchemy.ext.asyncio import AsyncEngine
import models
from routes import retrain,auth,userInput,predict
from typing import Annotated


load_dotenv(dotenv_path=Path(
    __file__).resolve().parent / ".env", override=True)


app = FastAPI()

origins = [
    "http://localhost:5173",
    "https://127.0.0.1:5173",
    "http://localhost"
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# DB table creation
models.Base.metadata.create_all(bind=engine)

# Routers
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(retrain.router)
app.include_router(userInput.router)



@app.on_event("startup")
async def startup_event():
    print("Application startup: Initializing database...")
    try:
         async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
    finally:
        await conn.close()  # Ensure the connection is closed after use
    print("Application startup: Database tables created (or already exist).")


@app.on_event("shutdown")
async def shutdown_event():
    print("Application shutdown: Disposing database engine...")
    await engine.dispose()  # Properly closes all pooled connections
    print("Application shutdown: Database engine disposed.")

    
        
        
   


