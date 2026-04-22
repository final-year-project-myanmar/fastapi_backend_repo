
from fastapi import  HTTPException, status
from app.utils.load_model import get_model
from app.repository.db import db_dependency
from app.schemas.schemas import SentimentResult, Probabilities
from app.repository.dataLayer.sentiment_results import insert_sentiment_results




def predict_sentiment(model, text):
    """
    Predict sentiment for a single text using preloaded model
    Args:
        model: The preloaded model from app.state
        text (str): Input text to classify
    Returns:
        dict: Prediction results
    """
        
    # Make prediction
    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0] if hasattr(
        model, 'predict_proba') else None

    # Map prediction to label
    label_map = {0: 'Neutral', 1: 'Positive', -1: 'Negative'}
    predicted_label = label_map.get(prediction, 'Unknown')

    result = {
        'text': text,
        'predicted_class': int(prediction),
        'predicted_label': predicted_label
    }

    if probabilities is not None:
        result['probabilities'] = {
            'class_0': float(probabilities[0]),
            'class_1': float(probabilities[1]),
            'class_-1': float(probabilities[2]) if len(probabilities) > 2 else 0.0
        }

    return result


async def process_text_for_sentiment(
    text: str,
    db: db_dependency,
    user_id: int,
    model: any
) -> SentimentResult:
    """
    Process the sentiment analysis for the given text, and save the result to the database.
    """
    # Perform sentiment analysis
    # Use model here
    analysis_result = await perform_sentiment_analysis(text, model)
    confidence = analysis_result['probabilities'].get(
        f"class_{analysis_result['predicted_class']}", 0.0
    )

    # Create SentimentResult object
    sentiment_result = SentimentResult(
        text=text,
        predicted_label=analysis_result['predicted_label'],
        predicted_class=analysis_result['predicted_class'],
        probabilities=Probabilities(
            class_0=analysis_result['probabilities'].get('class_0', 0.0),
            class_1=analysis_result['probabilities'].get('class_1', 0.0),
            class_minus_1=analysis_result['probabilities'].get('class_-1', 0.0)
        ),
        confidence=confidence
    )

    # Insert the result into the database
    insert_db = await insert_sentiment_results(db, sentiment_result, user_id)
    if not insert_db:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to insert sentiment result into the database."
        )

    return sentiment_result

async def perform_sentiment_analysis(text: str, model: any) -> dict:
    """
    Perform sentiment analysis using the injected model.

    Args:
        text (str): The input text to classify.
        model (any): The preloaded model.

    Returns:
        dict: Sentiment analysis results.
    """
    if(model is None):
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ML model is not loaded"
        )
    result = predict_sentiment(model, text)  # Use the model from dependency
    if not result:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ML model failed to analyze"
        )
    return result
