from pydantic_settings import BaseSettings, SettingsConfigDict
import boto3
from botocore.config import Config

class AWS_Settings(BaseSettings):
    AWS_REGION: str
    AWS_ACCESS_KEY_ID: str
    AWS_SECRET_ACCESS_KEY: str
    AWS_S3_BUCKET_NAME: str

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",    
        case_sensitive=True
    )


AWS_settings = AWS_Settings()

s3_client = boto3.client(
    "s3",
    region_name=AWS_settings.AWS_REGION,
    aws_access_key_id=AWS_settings.AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_settings.AWS_SECRET_ACCESS_KEY,
    config=Config(signature_version="s3v4"),
)


