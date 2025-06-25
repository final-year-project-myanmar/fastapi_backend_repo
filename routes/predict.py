from fastapi import APIRouter,Depends,HTTPException
from sqlalchemy.orm import Session
from schemas.schemas import *
from models import SentimentRequests
from utils.auth import get_current_user,get_current_user_optional
from core.db import SessionLocal
from typing import List,Optional
import joblib,os

router= APIRouter()
model_path = os.path.join(os.path.dirname(__file__), '..', 'LLMmodels', 'best_model_logistic_regression_bow_20250615_133524.pkl')

# DB Session dependency
def get_db():
   db=SessionLocal()
   try:
      yield db
   finally:
      db.close()
      


try:
    model = joblib.load(model_path)
    print("✅ Sentiment model loaded successfully.")
except Exception as e:
    model = None
    print(f"❌ Failed to load model: {e}")

@router.post("/predict",response_model=PredictResponse)
def predict_sentiment(
    req:PredictRequest,
    db:Session=Depends(get_db),
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
        sentiment_request=SentimentRequests(
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
def get_sentiments(
    db: Session = Depends(get_db),
    current_user = Depends(get_current_user)
):
    results = (
        db.query(SentimentRequests)
        .filter(SentimentRequests.user_id == current_user.user_id)
        .order_by(SentimentRequests.created_at.desc())
        .all()
    )

    return [
        PredictResponse(
            text=item.input_text,
            sentiment=item.sentiment,
            confidence=item.confidence_score,
           
        )
        for item in results
    ]
