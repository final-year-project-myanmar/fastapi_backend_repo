
import enum
from sqlalchemy import Column, ForeignKey, Integer, String, DateTime, Text, Float, func
from core.db import Base
from sqlalchemy import Enum as SQLEnum
from sqlalchemy import UniqueConstraint



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
    created_at=Column(DateTime(timezone=True), server_default=func.now())
    updated_at=Column(DateTime(timezone=True),onupdate=func.now())
    reset_token=Column(String,nullable=True)
    reset_token_expiration=Column(DateTime,nullable=True)



class account_status_types(enum.Enum):
    active = 'ACTIVE'
    revoke = 'REVOKE'
    

class APIKeys(Base):
    __tablename__ = 'api_keys'
    

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    keyname = Column(Text, nullable=False)
    account_status = Column(SQLEnum(account_status_types, name="account_status"))
    public_key = Column(Text,unique=True)
    hashkey= Column(Text, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    lastused_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
    __table_args__ = (
        UniqueConstraint('user_id','keyname',name='unq_usr_id_keyname'),
        )

class sentiment_types(enum.Enum):
    POSITIVE = "positive"
    NEGATIVE = "negative"
    NEUTRAL = "neutral"

class sentiment_result(Base):
    __tablename__ = 'sentiment_results'

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    input_text = Column(Text, nullable=False)
    sentiment = Column(SQLEnum(sentiment_types, name="sentiment"), default=sentiment_types.NEUTRAL)
    confidence_score = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    

