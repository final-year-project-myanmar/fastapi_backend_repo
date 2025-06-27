
from models import APIKeys as api_key_db
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.schemas import  Api_Key as api_key_achema

async def insert_sentiment_results(
    db: AsyncSession,
    sentiment_data: api_key_achema,
    user_id: int
):
    """
    Function to insert api key into the database.
    """
    pass
