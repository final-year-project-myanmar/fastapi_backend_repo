
from models import sentiment_result as sentiment_resultDB#DB_table
from schemas.schemas import SentimentResult #Response_Schema
from models import sentiment_types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

async def insert_sentiment_results(
    db: AsyncSession,
    sentiment_data: SentimentResult,
    user_id: int 
):
    """
    Function to insert sentiment results into the database.
    """
    sentiment_str = sentiment_data.predicted_label.lower()
    sentiment_enum = sentiment_types(sentiment_str)
    new_result = sentiment_resultDB(
        user_id=user_id,
        input_text=sentiment_data.text,
        sentiment=sentiment_enum,
        # sentiment=sentiment_types.POSITIVE,
        confidence_score=sentiment_data.confidence
    )

    db.add(new_result)
    await db.commit()
    await db.refresh(new_result)
    return new_result


async def get_all_sentiment_results(db: AsyncSession, user_id:int):
    """
    Function to get all sentiment results from the database.
    """
    query = select(sentiment_resultDB).where(
        sentiment_resultDB.user_id == user_id)
    result = await db.execute(query)
    # Fetch all results from the query (scalars will return the ORM objects)
    sentiment_records = result.scalars().all()
    
    return sentiment_records
    