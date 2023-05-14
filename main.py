from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi_limiter import FastAPILimiter
import redis.asyncio as redis

from fastapi.middleware.cors import CORSMiddleware

from src.config.config import settings
from src.database.db import get_db
from src.routes import users

app = FastAPI()


# @app.on_event("startup")
# async def startup():
#     """
#     Set limitation of requests on server
#
#     :return: None
#     """
#     r = await redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)
#     await FastAPILimiter.init(r)


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """
    Main page

    :return: Hello world message
    :rtype: dict
    """
    return {"message": "Hello World"}


@app.get("/api/healthchecker")
def healthchecker(db: Session = Depends(get_db)):
    """
    Checks work of database

    :param db: Database session
    :type db: Session
    :return: Welcome message
    :rtype: dict
    """
    try:
        # Make request
        result = db.execute(text("SELECT 1")).fetchone()
        if result is None:
            raise HTTPException(status_code=500,
                                detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to database")


# TODO: Add all routes in app
app.include_router(users.user_router, prefix='/api')