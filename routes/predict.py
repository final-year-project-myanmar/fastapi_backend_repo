from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import *
from models import sentiment_result
from utils.auth import get_current_user,get_current_user_optional
from core.db import AsyncSessionLocal,db_dependency
from typing import List,Optional
import joblib,os
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select


router= APIRouter()
model_path = os.path.join(os.path.dirname(__file__), '..', 'LLMmodels', 'best_model_logistic_regression_bow_20250615_133524.pkl')



try:
    model = joblib.load(model_path)
    print("✅ Sentiment model loaded successfully.")
except Exception as e:
    model = None
    print(f"❌ Failed to load model: {e}")

@router.post("/predict",response_model=PredictResponse)
async def predict_sentiment(
    req:PredictRequest,
    db:db_dependency,
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
):
    if model is None:
        raise HTTPException(status_code=500,detail="Sentiment model not loaded")
    
    # predict 
    text=req.text
    prediction= model.predict([text])[0]
    proba= model.predict_proba([text])[0] if hasattr(model,'predict_proba') else None
    label_map={0:"Neutral",1:"Positive",-1:"Negative"}
    label=label_map.get(prediction,"Unknown")
    confidence= max(proba) if proba is not None else None
    
    # save to DB
    if current_user:
        sentiment_request = sentiment_result(
            user_id=current_user.user_id,
            input_text=text,
            sentiment=label,
            confidence_score=confidence
        )
        db.add(sentiment_request)
        db.commit()
    # db.refresh(sentiment_request)

    #Return prediction 
    return PredictResponse(
        text=text,
        sentiment=label,
        confidence=confidence
    )


@router.get("/sentiments", response_model=List[PredictResponse])
async def get_sentiments(
    db: db_dependency,
    current_user = Depends(get_current_user)
):
    stmt = (
        select(sentiment_result)
        .where(sentiment_result.user_id == current_user.user_id)
        .order_by(sentiment_result.created_at.desc())
    )
    result = await db.scalars(stmt)
    rows = result.all()

    return [
        PredictResponse(
            text=item.input_text,
            sentiment=item.sentiment,
            confidence=item.confidence_score,
        )
        for item in rows
    ]