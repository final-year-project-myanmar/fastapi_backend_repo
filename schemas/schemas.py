from pydantic import BaseModel,EmailStr
from typing import Optional

class TestingBase(BaseModel):
   title:str

class TestingResponse(BaseModel):
   id:int
   title:str

   model_config = {
    "from_attributes": True
    }
   
class UserCreate(BaseModel):
    username:str
    email:EmailStr
    password:str

class UserLogin(BaseModel):
    email:EmailStr
    password:str

class ShowUsers(BaseModel):
    id:int
    username: str
    email: EmailStr
    model_config = {
    "from_attributes": True
    }

class Token(BaseModel):
    access_token:str
    token_type:str

class TokenData(BaseModel):
    username: Optional[str] = None
    #added
    user_id:Optional[int]=None

class ResetPasswordRequest(BaseModel):
    email: EmailStr
   
class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

class GoogleToken(BaseModel):
    id_token:str

class PredictRequest(BaseModel):
    text:str

class PredictResponse(BaseModel):
    text:str
    sentiment:str
    confidence:float | None



    