import csv
import io
from typing import List, Optional

from starlette import status
from fastapi import APIRouter, HTTPException, Depends
from app.repository.db import db_dependency
from app.schemas.schemas import UserInputRequest, OverAllSentimentResult, SentimentResult, DBSentimentResult, DBSentimentResultReponse, TokenData
from app.utils.userInput import process_text_for_sentiment
from app.utils.load_model import get_model
from app.repository.dataLayer.sentiment_results import get_all_sentiment_results
from app.utils.sentiment_results import map_db_sentiment_to_pydantic
from app.utils.auth import get_current_user, get_current_user_optional

router = APIRouter()


@router.post("/userinput", status_code=status.HTTP_201_CREATED, response_model=OverAllSentimentResult)
async def submit_user_input(input_data: UserInputRequest, db: db_dependency, model=Depends(get_model), current_user: Optional[TokenData] = Depends(get_current_user_optional)):
    """
    Endpoint to handle user input.
    """
    print(f"Current User: {current_user}")
    user_id = current_user.user_id if current_user else None
    all_results: List[SentimentResult] = []
    if input_data.text:

        # perform the sentiment analysis process with input_data.text
        sentiment_result = await process_text_for_sentiment(
            input_data.text, db, user_id, model
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
                    analysis_result = await process_text_for_sentiment(text_to_analyze, db, user_id, model)
                    all_results.append(analysis_result)

    elif not input_data.text and not input_data.uploadedFiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input: Please provide either text or files."
        )

    return {
        "message": "Sentiment analysis completed successfully.",
        "results": all_results
    }


@router.get("/userinput", status_code=status.HTTP_200_OK, response_model=DBSentimentResultReponse)
async def get_user_iput_sentiment_data(db: db_dependency, current_user: Optional[TokenData] = Depends(get_current_user)):
    """ End point to get all sentiment data from user input """

    all_results: List[DBSentimentResult] = await get_all_sentiment_results(db, current_user.user_id)
    pydantic_formatted_results = [
        map_db_sentiment_to_pydantic(record) for record in all_results
    ]

    return {
        "message": "Sentiment data retrieved successfully",
        "results": pydantic_formatted_results
    }
