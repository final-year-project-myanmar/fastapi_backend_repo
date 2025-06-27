import csv
import io
import os
from typing import List, Optional


from LLMmodels.deploy_model_20250615_133439 import predict_sentiment
from pydantic import BaseModel, Field
from starlette import status
from schemas.schemas import UserInputRequest, SentimentResult, Probabilities, OverAllSentimentResult, TokenData, DBSentimentResult, DBSentimentResultReponse
from fastapi import APIRouter, HTTPException, Depends
from core.dataLayer.sentiment_results import insert_sentiment_results, get_all_sentiment_results
from core.db import db_dependency
from utils.auth import get_current_user,get_current_user_optional

from utils.sentiment_results import map_db_sentiment_to_pydantic

router = APIRouter()


async def perform_sentiment_analysis(text: str):
    # Placeholder for sentiment analysis logic
    result = predict_sentiment(text)
    return result

# helper function for processing sentiment analysis and save to db object


async def process_text_for_sentiment(
    text: str,
    db: db_dependency,
    user_id: int
) -> SentimentResult:

    analysis_result = await perform_sentiment_analysis(text)
    confidence = analysis_result['probabilities'].get(
        f"class_{analysis_result['predicted_class']}", 0.0)

 # Create SentimentResult object
    sentiment_result = SentimentResult(
        text=text,
        predicted_label=analysis_result['predicted_label'],
        predicted_class=analysis_result['predicted_class'],
        probabilities=Probabilities(
            class_0=analysis_result['probabilities'].get(
                'class_0', 0.0),
            class_1=analysis_result['probabilities'].get(
                'class_1', 0.0),
            class_minus_1=analysis_result['probabilities'].get(
                'class_-1', 0.0)
        ),
        confidence=confidence
    )
    await insert_sentiment_results(db, sentiment_result, user_id)
    return sentiment_result


@router.post("/userinput", status_code=status.HTTP_201_CREATED, response_model=OverAllSentimentResult)
async def submit_user_input(input_data: UserInputRequest, db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user_optional)):
    """
    Endpoint to handle user input.
    """
    print(f"Current User: {current_user}")
    user_id = current_user.user_id if current_user else None
    all_results: List[SentimentResult] = []
    if input_data.text:

        # perform the sentiment analysis process with input_data.text
        sentiment_result = await process_text_for_sentiment(
            input_data.text, db, user_id
        )
        all_results.append(sentiment_result)

        # multiple files case
    elif input_data.uploadedFiles:
        for file in input_data.uploadedFiles:
            csv_file = io.StringIO(file)
            reader = csv.reader(csv_file)

            # read the rowdata from the files
            for row_data in reader:
                if row_data:
                    text_to_analyze = row_data[0]

                    # perform the sentiment analysis process with input_data.uploadedFiles's rowdata
                    analysis_result = await process_text_for_sentiment(text_to_analyze, db, user_id)
                    all_results.append(analysis_result)

    elif not input_data.text and not input_data.uploadedFiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input: Please provide either text or files."
        )

    return {
        "message": "Files processed",
        "results": all_results
    }


@router.get("/userinput", status_code=status.HTTP_200_OK, response_model=DBSentimentResultReponse)
async def get_user_iput_sentiment_data(db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user)):
    """ End point to get all sentiment data from user input """
    
    all_results = await get_all_sentiment_results(db, current_user.user_id)

    pydantic_formatted_results = [
        map_db_sentiment_to_pydantic(record) for record in all_results
    ]

    return {
        "message": "Sentiment data retrieved successfully",
        "results": pydantic_formatted_results
    }
