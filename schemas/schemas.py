from pydantic import BaseModel,EmailStr, Field
from typing import Optional,List

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
    user_id:Optional[int]=None



class ResetPasswordRequest(BaseModel):
    email: EmailStr
   
class ResetPasswordConfirm(BaseModel):
    token: str
    new_password: str

class GoogleToken(BaseModel):
    id_token:str


class Api_Key(BaseModel):
    key_name : str
    public_key: str
    hashkey :str


class PredictRequest(BaseModel):
    text:str

class PredictResponse(BaseModel):
    text:str
    sentiment:str
    confidence:float | None


class Probabilities(BaseModel):
    class_0: float
    class_1: float
    class_minus_1: float = Field(default=0.0, alias='class_-1')


class SentimentResult(BaseModel):
    text: str
    predicted_label: str
    predicted_class: int
    probabilities: Probabilities
    confidence: float


class OverAllSentimentResult(BaseModel):
    message: str
    results: List[SentimentResult]

class DBSentimentResult(BaseModel):
    text:str
    sentiment: str
    confidence : float
    user_id : Optional[int]
    

class DBSentimentResultReponse(BaseModel):
    message: str
    results: List[DBSentimentResult]

    
class UserInputRequest(BaseModel):
    text: str = ""
    uploadedFiles: Optional[List[str]] = Field(default_factory=list)


