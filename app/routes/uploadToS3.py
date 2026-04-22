from app.schemas.schemas import AWS_PreSigned_Response, AWS_PreSigned_Request
from fastapi import APIRouter, HTTPException, UploadFile, Depends, File
from app.settings import AWS_settings, s3_client
from uuid import uuid4
import re  

def sanitize(filename: str) -> str:
    """
    Sanitize the filename by removing unwanted characters.
    """
    return re.sub(r'[^a-zA-Z0-9_.-]', '', filename) 

router = APIRouter(prefix="/upload", tags=["upload"])

def get_s3_client():
    """
    Dependency to get the S3 client.
    This can be used in route handlers to access the S3 client.
    """
    return s3_client

@router.post("/presigned_url", response_model=AWS_PreSigned_Response)
async def get_presigned_url(file: UploadFile = File(...),
                            s3 = Depends(get_s3_client)):
    """
    Generate a pre-signed URL for uploading files to S3.
    """
    try:  
        bucket_name = AWS_settings.AWS_S3_BUCKET_NAME
        key = f"uploads/{sanitize(file.filename)}"
        
        response = s3.generate_presigned_url(
            'put_object',
            Params={'Bucket': bucket_name, 'Key': key, 'ContentType': file.content_type},
            ExpiresIn=3600  # URL expires in 1 hour
        )
        return AWS_PreSigned_Response(url=response, key=key, bucket=bucket_name)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

