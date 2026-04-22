
import datetime
import os
import joblib
import wandb
from fastapi import Request
import logging

logger = logging.getLogger("uvicorn.error")


def load_model():
    try:
        # Load model from WandB
        WANDB_LOGIN_KEY = os.environ.get('WANDB_LOGIN_KEY')
        wandb.login(key=WANDB_LOGIN_KEY)
        run = wandb.init(project='my_fastapi_backend_repo',
                        name=f"{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}+training_run")

        artifact = run.use_artifact(
            'ayenyeinsan2904-chiang-mai-university-org/wandb-registry-model/senior_project_myanmar_senti:latest', type='model')
        artifact_dir = artifact.download()

        print(f"Artifact downloaded to: {artifact_dir}")

        
        model = None
        for file in os.listdir(artifact_dir):
            print(f"Found file: {file}")
            if file.endswith('.h5') or file.endswith('.pkl'):
                modelpath = os.path.join(artifact_dir, file)
                print(f"Model file found: {modelpath}")
                break


       
        model = joblib.load(modelpath)
        logger.info("Loaded model: %s | has predict_proba=%s",
                    type(model), hasattr(model, "predict_proba"))
        if model is None:
            raise ValueError("Model could not be loaded.")
        print(f"✅ Sentiment model loaded successfully." )
            
            
    except Exception as e:
            model = None
            logger.exception("❌ Failed to load model")
            print(f"❌ Failed to load model: {e.__class__.__name__}: {e}")
        
    finally:
            try:
              if run is not None:
                run.finish()
            except Exception:
             pass
        
    return model


def get_model(request: Request) -> any:
    """
    Dependency to access the preloaded model stored in app.state.
    """
    return request.app.state.model




