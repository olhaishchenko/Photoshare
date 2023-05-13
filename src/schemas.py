from pydantic import BaseModel, Field, EmailStr
from pydantic.types import date

class UserDb(BaseModel):
    id: int
    username: str
    email: EmailStr