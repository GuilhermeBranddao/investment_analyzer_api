from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class User(BaseModel):
    id: Optional[int] = None
    name: str
    password: str
    email: str
    is_active: Optional[int] = 1

    class Config:
        orm_mode = True

class UserBasic(BaseModel):
    id: Optional[int] = None
    name: str
    email: str

    class Config:
        orm_mode = True

class LoginSuccess(BaseModel):
    user: UserBasic
    access_token: str

class LoginData(BaseModel):
    username: str
    password: str
