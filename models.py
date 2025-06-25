from sqlalchemy import Column,ForeignKey,Integer,Float,String,DateTime,Text,func
from core.db import Base

class Testing(Base):
    __tablename__='testing'
    id=Column(Integer,primary_key=True,index=True)
    title=Column(String,index=True)

class User(Base):
    __tablename__ = 'users'

    id=Column(Integer, primary_key=True, index=True)
    username= Column(String(52),unique=True,nullable=False)
    email=Column(String(255),unique=True,nullable=False)
    password=Column(Text,nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    reset_token=Column(String,nullable=True)
    reset_token_expiration=Column(DateTime,nullable=True)

class SentimentRequests(Base):
    __tablename__="sentimentRequests"

    id=Column(Integer,primary_key=True,index=True)
    user_id=Column(Integer,ForeignKey("users.id"),nullable=False)
    input_text=Column(Text,nullable=False)
    sentiment = Column(Text, nullable=False)
    confidence_score = Column(Float, nullable=False)
    created_at=Column(DateTime(timezone=True),server_default=func.now())

