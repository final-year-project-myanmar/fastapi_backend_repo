from fastapi import APIRouter, HTTPException,Depends,Request
from starlette import status
from schemas.schemas import Api_Key as api_key_achema
from utils.auth import get_current_user
from typing import List, Optional
from schemas.schemas import TokenData
router = APIRouter()




@router.post("/api_key_creation")
async def create_api_key(request: Request):
    data = await request.json()
    print(data)
    return {"received": data}
