import os
from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from typing import Annotated
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import Session
from fastapi import  Depends
# load .env file
load_dotenv()

# get variables from environment
POSTGRES_URL_NON_POOLING=os.getenv("POSTGRES_URL_NON_POOLING")
POSTGRES_URL_NON_POOLING_ASYNC = os.getenv("POSTGRES_URL_NON_POOLING_ASYNC")
POSTGRES_USER=os.getenv("POSTGRES_USER")
POSTGRES_HOST=os.getenv("POSTGRES_HOST")
POSTGRES_PORT=os.getenv("POSTGRES_PORT")
SUPABASE_JWT_SECRET=os.getenv("SUPABASE_JWT_SECRET")

POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_DATABASE = os.getenv("POSTGRES_DATABASE")

# DATABASE_URL=f"postgresql://{POSTGRES_USER}:{POSTGRES_PASSWORD}@{POSTGRES_HOST}:{POSTGRES_PORT}/{POSTGRES_DATABASE}"
DATABASE_URL=POSTGRES_URL_NON_POOLING
DATABASE_URL_ASYNC= POSTGRES_URL_NON_POOLING_ASYNC

#Testing Database URL
TEST_DATABASE_URL = os.getenv("TEST_DATABASE_URL")


#Setup Test database URL
test_engine = create_engine(TEST_DATABASE_URL, echo=True)
Test_Async_Session_Local = sessionmaker(autocommit=False, autoflush=False,
                                 bind=test_engine, class_=AsyncSession, expire_on_commit=False)

#Async production database engine setup
engine = create_async_engine(DATABASE_URL_ASYNC, echo=True)
Async_Session_Local = sessionmaker(autocommit=False, autoflush=False,
                                 bind=engine, class_=AsyncSession, expire_on_commit=False)

# Synchronous database engine setup
# engine = create_engine(DATABASE_URL)
# SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base=declarative_base()

#Dependency to get the production database session [Production purposes]
async def get_db_session() -> AsyncSession:
    try:
     async with Async_Session_Local() as session:  
        yield session  
    finally:
        await session.close()

db_dependency = Annotated[AsyncSession, Depends(get_db_session)]

#Dependency to get the test database session [Testing purposes]
async def get_test_db_session() -> AsyncSession:
    try:
        async with Test_Async_Session_Local() as session:
            yield session
    finally:
        await session.close()

test_db_dependency = Annotated[AsyncSession, Depends(get_test_db_session)]


