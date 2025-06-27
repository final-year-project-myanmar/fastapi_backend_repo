from passlib.context import CryptContext
from datetime import datetime,timedelta
from dotenv import load_dotenv
from jose import jwt,JWTError
from fastapi.security import OAuth2PasswordBearer
from fastapi import Depends,HTTPException,Request
from typing import Optional
from schemas.schemas import TokenData
import os


# load .env file
load_dotenv()

# get variables from environment
SECRET_KEY=os.getenv("SECRET_KEY")
ALGORITHM=os.getenv("ALGORITHM")
try:
    ACCESS_TOKEN_EXPIRED_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRED_MINUTES", "15"))
except ValueError:
    raise ValueError("ACCESS_TOKEN_EXPIRED_MINUTES must be an integer.")

# password hashing context
pwd_context= CryptContext(schemes=['bcrypt'],deprecated='auto')
# OAuth2 scheme
oauth2_scheme= OAuth2PasswordBearer(tokenUrl="/login")

def hash_password(password:str)->str:
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

# JWT token creation 
def generate_token(data:dict):
    to_encode= data.copy()
    expire= datetime.utcnow()+ timedelta(minutes=int(ACCESS_TOKEN_EXPIRED_MINUTES))
    to_encode.update({"exp":expire})
    encoded_jwt= jwt.encode(to_encode,SECRET_KEY,algorithm=ALGORITHM)
    return encoded_jwt



def get_current_user(token:str=Depends(oauth2_scheme))->TokenData:
    print(f"Token received in get_current_user: {token[:30]}...")
    credentials_exception= HTTPException(
        status_code=401,
        detail="Invalid auth credentials",
        headers={'WWW-Authenticate':"Bearer"},

    )
    try:
        payload= jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])

        print("Decoded JWT payload:", payload)
        #added 
        user_id:int=payload.get("user_id")
        email:str= payload.get('sub')
        print(user_id,email)
        if user_id is None or email is None:
            raise credentials_exception
        return TokenData(username=email,user_id=user_id)
    except JWTError as e:
        print(f"JWT Error during decode: {e}")
        raise credentials_exception
    except Exception as e:
        print(f"Unexpected error in get_current_user: {e}")

        raise credentials_exception

def get_current_user_optional(request:Request)->Optional[TokenData]:
    auth_header=request.headers.get("Authorization")
    if not auth_header:
        return None
    
    scheme, _, token = auth_header.partition(" ")
    if scheme.lower() != "bearer" or not token:
        return None
    
    try:
        payload= jwt.decode(token,SECRET_KEY,algorithms=[ALGORITHM])
    
        user_id:int=payload.get("user_id")
        email:str= payload.get('sub')
        if user_id is None or email is None:
            raise credentials_exception
        return TokenData(username=email,user_id=user_id)
    except JWTError:
        raise None
