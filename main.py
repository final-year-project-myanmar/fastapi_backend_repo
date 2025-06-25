# main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.db import engine
import models
from routes import retrain, auth, predict,userInput

app = FastAPI()


models.Base.metadata.create_all(bind=engine)

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


    
    
    
        
        
   


