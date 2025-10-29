from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class User(BaseModel):
    id: Optional[int] = None
    name: str
    password: str
    email: str
    is_active: Optional[int] = 1

    # `from_attributes=True` é o equivalente ao `orm_mode=True`.
    model_config = ConfigDict(from_attributes=True)

class UserBasic(BaseModel):
    id: Optional[int] = None
    name: str
    email: str

    model_config = ConfigDict(from_attributes=True)

class LoginSuccess(BaseModel):
    user: UserBasic
    access_token: str

class LoginData(BaseModel):
    username: str
    password: str
