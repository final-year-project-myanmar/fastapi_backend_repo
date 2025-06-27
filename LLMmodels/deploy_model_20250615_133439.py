# Deployment Script for Sentiment Analysis Model
import joblib
import pandas as pd
import os

# Load the trained model
model_path = os.path.join(os.path.dirname(
    __file__), 'best_model_logistic_regression_bow_20250615_133439.pkl')
model = joblib.load(model_path)


def predict_sentiment(text):
    """
    Predict sentiment for a single text
    Args:
        text (str): Input text to classify
    Returns:
        dict: Prediction results
    """
    # Make prediction
    prediction = model.predict([text])[0]
    probabilities = model.predict_proba([text])[0] if hasattr(model, 'predict_proba') else None
    
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

def predict_batch(texts):
    """
    Predict sentiment for multiple texts
    Args:
        texts (list): List of texts to classify
    Returns:
        list: List of prediction results
    """
    return [predict_sentiment(text) for text in texts]

# Example usage
# if __name__ == "__main__":
#     # Test the model
#     sample_texts = [
#         "လီးရုပ်နဲ့ အရက်ဖောနေပီး",
#         "မတန်ဘူးဗျ ၄၀၀၀နဲ့ ထည့်ပေးတဲ့ဟင်းနှစ်မျိုးက နည်းနည်းလေး အရင်တည်းက နည်းတာမဖြူဆိုင်က အရင်ကတော့ ၁၆၀၀နဲ့တန်တယ် အခုတော့မတန်တော့ဘူး",
#         "အားပေးနေပါတယ်"
#     ]
    
#     for text in sample_texts:
#         result = predict_sentiment(text)
#         print(f"Text: {result['text']}")
#         print(f"Prediction: {result['predicted_label']} ({result['predicted_class']})")
#         if 'probabilities' in result:
#             print(f"Probabilities: {result['probabilities']}")
#         print("-" * 50)
