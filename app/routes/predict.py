from fastapi import APIRouter,Depends,HTTPException,Request
from app.schemas.schemas import *
from app.models import sentiment_result
from app.utils.auth import get_current_user,get_current_user_optional
from app.repository.db import db_dependency
from typing import List,Optional
from sqlalchemy import select
from app.utils.load_model import get_model
from fastapi.security.api_key import APIKeyHeader
from app.repository.dataLayer.api_keys_layer import check_if_token_exists



router= APIRouter()
Api_Key_header = APIKeyHeader(name="X-Api-Key", auto_error=False)
label_map = {0: "Neutral", 1: "Positive", -1: "Negative"}

@router.post("/predict",response_model=PredictResponse)
async def predict_sentiment(
    req:PredictRequest,
    db:db_dependency,
    api_key: str = Depends(Api_Key_header),
    model= Depends(get_model),
    current_user: Optional[TokenData] = Depends(get_current_user_optional)
    
):
    if model is None:
        raise HTTPException(status_code=500,detail="Sentiment model not loaded")
    
    check_if_token_exists_result = await check_if_token_exists(db,api_key)
    if not check_if_token_exists_result:
        raise HTTPException(status_code=401, detail="Invalid API Key")
    print(f">>> API Key found: {check_if_token_exists_result}")
        
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

@router.post("/predictFile", response_model=PredictMultipleResponse)
async def predict_multiple_file(req: PredictMultipleRequest,
                                db: db_dependency,
                                api_key: str = Depends(Api_Key_header),
                                model=Depends(get_model),
                                current_user: Optional[TokenData] = Depends(get_current_user_optional)):
    
    if model is None:
        raise HTTPException(status_code=500, detail="Sentiment model not loaded")
    check_if_token_exists_result = await check_if_token_exists(db,api_key)
    if not check_if_token_exists_result:
        raise HTTPException(status_code=401, detail="Invalid API Key")
   
   #Predict
    if req.text is None:
        raise HTTPException(status_code=500, detail = "There is no text input to analyze")
    
    results = []
    multiple_text = req.text
    for text in multiple_text:
        prediction = model.predict([text])[0]
        proba = model.predict_proba([text])[0] if hasattr(
        model, 'predict_proba') else None
        label = label_map.get(prediction, "Unknown")
        confidence = max(proba) if proba is not None else None
        
        results.append({
            "text": text,
            "sentiment": label,
            "confidence": confidence
          })
           
        
    
    # Return prediction
    return PredictMultipleResponse( results= results )

