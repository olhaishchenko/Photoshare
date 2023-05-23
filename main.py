from fastapi import FastAPI, Depends, HTTPException
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware
from slowapi.util import get_remote_address
from sqlalchemy.orm import Session
from sqlalchemy import text
from fastapi_limiter import FastAPILimiter, default_identifier
import redis.asyncio as redis
import uvicorn
from fastapi_limiter.depends import RateLimiter

from fastapi.middleware.cors import CORSMiddleware

from src.config.config import settings
from src.routes import auth, users, comments, pictures
from src.database.db import get_db

app = FastAPI()


@app.on_event("startup")
async def startup():
    """
    Set limitation of requests on server

    :return: None
    """


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


app.include_router(auth.router, prefix='/api')
app.include_router(users.user_router, prefix='/api')
app.include_router(comments.router, prefix='/api')
app.include_router(pictures.router, prefix='/api')

if __name__ == "__main__":
    uvicorn.run(app, host="localhost", port=8000)
