import csv
import os
import io  
from typing import List, Optional

from pydantic import BaseModel,Field
from fastapi import APIRouter, HTTPException
from starlette import status
router = APIRouter()


class UserInputRequest(BaseModel):
    text: str = ""
    uploadedFiles: Optional[List[str]] = Field(default_factory=list)


class SentimentResult(BaseModel):
    id: str
    text: str
    sentiment: str
    confidence: float


async def perform_sentiment_analysis(text: str):
    # Placeholder for sentiment analysis logic
    # This function should implement the actual sentiment analysis process
    pass


@router.post("/userinput", status_code=status.HTTP_201_CREATED)
async def submit_user_input(input_data: UserInputRequest):
    """
    Endpoint to handle user input.
    """
    print(f"Received input: {input_data}")
    if input_data.text:
        print(f"Received text: {input_data.text}")

        # perform the sentiment analysis process with input_data.text

        return {"message": "Text received", "text": input_data.text}
    elif input_data.uploadedFiles:
        print(f"Received files: {input_data.uploadedFiles}")

        for file in input_data.uploadedFiles:
            print(f"Processing file: {file}")
            csv_file = io.StringIO(file)
            reader = csv.reader(csv_file)
            print(f"Reader: {reader}")

            for row_data in reader:
                if row_data:  
                    text_to_analyze = row_data[0]
                    print(f"Analyzing CSV line: '{text_to_analyze[:100]}...'")
                   
                else:
                    print("Skipping empty row in CSV.")

        # read the rowdata from the files
        # perform the sentiment analysis process with input_data.uploadedFiles's rowdata

        return {"message": "Files received", "files": input_data.uploadedFiles}
    elif not input_data.text and not input_data.uploadedFiles:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid input: Please provide either text or files."
        )
