#データ型の定義
from pydantic import BaseModel
from typing import Optional
from decouple import config

CSRF_KEY = config('CSRF_KEY')

class CsrfSettings(BaseModel):
  secret_key: str = "asecrettoeverybody"

class Daily(BaseModel):
    id: str
    date: str
    weight: float

class DailyBody(BaseModel):
    date: str
    weight: float

class SuccessMsg(BaseModel):
    message: str

class UserBody(BaseModel):
    email: str
    password: str

class UserInfo(BaseModel):
    id: Optional[str] = None
    email:str

class Csrf(BaseModel):
    csrf_token : str