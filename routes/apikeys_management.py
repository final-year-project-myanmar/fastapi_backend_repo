
from fastapi import APIRouter, HTTPException, Depends, Request
from starlette import status
from schemas.schemas import Api_Key as api_key_achema, Api_KeyDBResponse
from utils.auth import get_current_user, hash_password
from typing import List, Optional
from schemas.schemas import TokenData
from core.dataLayer.api_keys_layer import insert_new_api_key, get_api_key_info_from_user, check_if_key_exists, delete_api_key
from core.db import db_dependency
import secrets

router = APIRouter()


@router.post("/api_key_creation", status_code=status.HTTP_201_CREATED)
async def create_api_key(request: api_key_achema, db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user)):
    
    key_name = request.key_name.strip()
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user to generate API key"
        )
    if not key_name:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key name is required."
        )

    # validate if key_name has already existed for current user
    existing_key = await check_if_key_exists(db, current_user.user_id, key_name)

    if existing_key:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"API key with  name '{key_name}' already exists for the user."
        )
    # generate public_key and hashkey
    hash_key = hash_password(key_name)
    public_key = f"pk-{hash_key[:10]}{secrets.token_urlsafe(32)}"

    api_key_obj = request.model_copy(update={
        "account_status": "active",
        "public_key": f"pk-{hash_key[:10]}{secrets.token_urlsafe(32)}",
        "hashkey": hash_key
    })

    # insert into DB table
    new_key = await insert_new_api_key(api_key_obj, db, current_user.user_id)

    print(f">>> New Key from DB: {new_key}")

    return {
        "message": "API Key Created!",
        "data": {
            "key_name":new_key.keyname,
            "public_key": new_key.public_key,
            "created_at": new_key.created_at,
            "lastused_at": new_key.lastused_at,
        }
    }


@router.delete("/api_key_delete", status_code=status.HTTP_200_OK)
async def delete_api_key_request(request: Request, db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user)):
    data = await request.json()

    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Unauthorized user to delete API key"
        )
    if not data.get("key_name"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="API key name is required to delete API key."
        )
    # delete api key from DB table
    api_key = await delete_api_key(db, current_user.user_id, data.get("key_name").strip())

    if api_key:
        await db.delete(api_key)
        await db.commit()
        return {"message": "API key deleted successfully."}
    else:
        return {"message": "API key not found."}


@router.get("/api_key", status_code=status.HTTP_200_OK,)
async def get_api_key(db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user)):

    print(f">>>> Current user:",current_user)
    # get from DB table
    get_key_info = await get_api_key_info_from_user(db, current_user.user_id)

    print(f">>> New Key from DB: {get_key_info}")

    return {
        "message": "API Key from User!",
        "data": [{

            "key_name": key.keyname,
            "public_key": key.public_key,
            "account_status": key.account_status,
            "created_at": key.created_at,
            "lastused_at": key.lastused_at

        } for key in get_key_info]

    }

