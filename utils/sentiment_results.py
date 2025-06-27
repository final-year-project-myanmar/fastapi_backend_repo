from models import sentiment_result as DBSentimentResult
from schemas.schemas import DBSentimentResult as SentimentSchemaFromDB



def map_db_sentiment_to_pydantic(db_result: DBSentimentResult) -> SentimentSchemaFromDB:
    return SentimentSchemaFromDB(
        text=db_result.input_text,
        sentiment=db_result.sentiment,
        confidence=db_result.confidence_score,
        user_id=db_result.user_id
     
    )
