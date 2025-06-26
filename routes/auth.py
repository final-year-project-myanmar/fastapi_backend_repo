from fastapi import APIRouter, HTTPException, Depends
from schemas.schemas import *
from sqlalchemy.orm import Session
from core.db import SessionLocal
from models import Testing,User
from utils.auth import *
from typing import List
import requests

router=APIRouter()


# DB Session dependency
def get_db():
   db=SessionLocal()
   try:
      yield db
   finally:
      db.close()

# Post endpoint
@router.post("/testing/",response_model=TestingResponse)
async def create_testing(test:TestingBase, db:Session=Depends(get_db)):
   db_test= Testing(title=test.title)
   db.add(db_test)
   db.commit()
   db.refresh(db_test)
   return db_test

# Get endpoint
@router.get("/testing/",response_model=List[TestingResponse])
async def get_testing(db:Session=Depends(get_db)):
   return db.query(Testing).all()

@router.post('/register',response_model=ShowUsers)
def register(user:UserCreate,db:Session=Depends(get_db)):
    existing_user=db.query(User).filter(User.email == user.email).first()
    if existing_user:
        raise HTTPException(status_code=400,detail="Email already exists")
    
    new_user=User(
        username=user.username,
        email=user.email,
        password=hash_password(user.password),
        
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

@router.post("/login")
def login(user:UserLogin,db:Session=Depends(get_db)):
    db_user=db.query(User).filter(User.email==user.email).first()
    if not db_user or not verify_password(user.password,db_user.password):
        raise HTTPException(status_code=401,detail="Invalid Email or password")
    access_token=generate_token(
        data={
            "sub":db_user.email,
            "user_id":db_user.id
            },
    )
    return {"access_token":access_token,"token_type":"bearer"}
    

@router.get("/profile",response_model=ShowUsers)
async def get_profile(
    user:TokenData=Depends(get_current_user),
    db:Session=Depends(get_db)
):
    user=db.query(User).filter(User.email==user.username).first()
    if not user:
        raise HTTPException(status_code=404,detail="User not found")
    return user

@router.post("/forgot-password")
def forgot_password(user:ResetPasswordRequest,db:Session=Depends(get_db)):
     db_user=db.query(User).filter(User.email==user.email).first()
     if not db_user:
         raise HTTPException(status_code=404,detail="Email not found")
     reset_token=generate_token(data={"sub":db_user.email})
   
      # Return the token for testing/dev purposes
     return{
            "message": "Password updated successfully",
             "reset_token": reset_token
     }

@router.post("/reset-password")
def reset_password(data: ResetPasswordConfirm,db:Session=Depends(get_db)):
    db_user=db.query(User).filter(User.email==data.email).first()
    if not db_user:
        raise HTTPException(status_code=404,detail="User not found")
    db_user.password=hash_password(data.new_password)
    db.commit()
    return {"message":"Password has been reset successfully"}
    
@router.post("/google-auth")
def google_login(token_data:GoogleToken,db:Session=Depends(get_db)):
    id_token= token_data.id_token
    try:
        google_resp = requests.get(f"https://oauth2.googleapis.com/tokeninfo?id_token={id_token}").json()
        if "email" not in google_resp:
            raise HTTPException(status_code=400, detail="Invalid Google token")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Google token verification failed: {str(e)}")

    user=db.query(User).filter(User.email==google_resp["email"]).first()
    if not user:
        user= User(username=google_resp.get("name","googleuser"),email=google_resp["email"],password="dummy")
        db.add(user)
        db.commit()
        db.refresh(user)
    access_token=generate_token({"sub":user.email,"user_id":user.id})
    return {
        "access_token": access_token,
        "user": {"username": user.username, "email": user.email},
        "token_type": "bearer"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")
