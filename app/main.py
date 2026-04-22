
import asyncio
import os
import pty
import signal
import subprocess
from contextlib import asynccontextmanager
from pathlib import Path

from dotenv import load_dotenv
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncEngine
from sqlalchemy.orm import Session, declarative_base

from app.repository.db import Base, engine, test_engine
from app.routes import (apikeys_management, auth, predict, retrain, uploadToS3,
                        userInput)
from app.settings import AWS_Settings, s3_client
from app.utils.api_services import CustomRateLimitMiddleware
from app.utils.load_model import load_model
from app.utils.terminalBackend import pty_to_ws, ws_to_pty
from fastapi import FastAPI, WebSocket, WebSocketDisconnect

load_dotenv(dotenv_path=Path(
    __file__).resolve().parent / ".env", override=True)

origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://localhost:8001",
    "http://localhost"
]
rate_limits = {
    "/predict": (5, 60),
}  # 5 requests per 60 seconds

@asynccontextmanager
async def lifespan(app: FastAPI):
    
    try:
        print("Loading ML model and initializing database...")
        #load model 
        app.state.model =  load_model()
        async with engine.begin() as conn:
             await conn.run_sync(Base.metadata.create_all)
       # Only run test DB init if in test mode
        if os.getenv("TESTING") == "1":
            async with test_engine.connect() as test_conn:
                await test_conn.run_sync(Base.metadata.create_all)
        print("Application startup: Database tables created (or already exist).")
        yield 
    finally:
        print("Application shutdown: Disposing database engine...")
        await engine.dispose()
        if test_engine:
            test_engine.dispose()  # Properly closes all pooled connections
        print("Application shutdown: Database engine disposed.")


app = FastAPI(title="MyanSen Language Processing API",lifespan=lifespan, contact={
    "name": "Ayen Nyein San",
    "email": "aye2904@gmail.com"})
        
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.add_middleware(CustomRateLimitMiddleware, limits=rate_limits)
# Routers
app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(retrain.router)
app.include_router(userInput.router)
app.include_router(apikeys_management.router)
app.include_router(uploadToS3.router, prefix="/api/v1")
# Dependency to access the preloaded model



@app.websocket("/ws")
async def ws_shell(ws: WebSocket):
    await ws.accept()

   
    master_fd, slave_fd = pty.openpty()

    
    env = os.environ.copy()
    env.update({"LANG": "en_US.UTF-8", "LC_ALL": "en_US.UTF-8"})
    
    # 2) Start an interactive shell attached to the PTY slave
    proc = subprocess.Popen(
        # interactive shell
        ["docker", "exec", "-i",
            "e9ef442cb3f98d648553c19a09646529b16b36a74213b39fc32ddd990aacffd4", "/bin/bash"],
        stdin=slave_fd,
        stdout=slave_fd,
        stderr=slave_fd,
        start_new_session=True,       
        close_fds=True,
        bufsize=0,   # no stdio buffering (PTY anyway)
        env=env
    )
   
    # Parent must close its copy of the slave
    os.close(slave_fd)
       
    # 3) Run both directions concurrently until one side stops
    reader_task = asyncio.create_task(pty_to_ws(master_fd,ws))
    writer_task = asyncio.create_task(ws_to_pty(master_fd,ws))

    # Wait for either task to complete
    done, pending = await asyncio.wait(
        [reader_task, writer_task],
        return_when=asyncio.FIRST_COMPLETED
    )

   # 4. Clean up resources
    print("Cleaning up PTY and subprocess...")
    for task in pending:
        task.cancel()  # Cancel the other task that is still running

    try:
        # Terminate the whole process group (the shell and any children it spawned)
        os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
    except ProcessLookupError:
        # The process might have already exited
        pass
    except Exception as e:
        print(f"Error during process cleanup: {e}")
