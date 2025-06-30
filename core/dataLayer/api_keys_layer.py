
from models import APIKeys as api_key_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas import Api_Key as api_key_achema, Api_KeyDBResponse
from sqlalchemy import select
from typing import List


async def insert_new_api_key(
    api_key: api_key_achema,
    db: AsyncSession,
    user_id: int
):
    """
    Function to insert api key into the database.
    """
    new_result = api_key_db(
        user_id=user_id,
        keyname=api_key.key_name,
        account_status = api_key.account_status,
        public_key = api_key.public_key,
        hashkey = api_key.hashkey
        
    )
    
    db.add(new_result)
    await db.commit()
    await db.refresh(new_result)
    return new_result


async def check_if_key_exists(db: AsyncSession,
                              user_id: int, keyname: str):
    """Function to check if API key already exists for the user."""

    
    query = select(api_key_db).where(
                api_key_db.user_id == user_id,
                api_key_db.keyname == keyname,
                
                                     )
    existing_key = await db.scalar(query)
    return existing_key
    

async def get_api_key_info_from_user(
    db: AsyncSession,
    user_id: int
) -> List[Api_KeyDBResponse]:
    """
    Function to get api key info of specific user.
    
    When someone use api,,,
    
    key.lastused_at = datetime.utcnow()
    session.add(key)
    await session.commit()
    
    """
    query = select(api_key_db).where(api_key_db.user_id == user_id)

    result = await db.execute(query)
    api_key_info = [
        Api_KeyDBResponse(
            keyname=key.keyname,
            public_key=key.public_key,
            account_status=key.account_status,
            created_at=key.created_at,
            lastused_at=key.lastused_at
        )
        for key in result.scalars().all()
    ]
    
    return api_key_info


async def delete_api_key(db: AsyncSession,
                         user_id: int,
                         keyname: str):
    """
    Function to delete api key from the database.
    
    """
    query = select(api_key_db).where(api_key_db.user_id == user_id,
                                     api_key_db.keyname == keyname)
    result = await db.execute(query)
    api_key = result.scalar_one_or_none()
    if api_key:
        await db.delete(api_key)
        await db.commit()
    else:
        raise ValueError("API key not found.")
    return api_key
    
