from turtle import title
from pydantic import BaseModel, EmailStr, Field

class UserBase(BaseModel):
  first_name: str = Field(None, title='First name', max_length=512)
  last_name: str = Field(None, title='First name', max_length=512)
  
class EmailUserBase(UserBase):
  email: EmailStr = Field(title = 'Email address')
  password: str = Field(title = 'Password')
  
class WalletUserBase(UserBase):
  wallet: str = Field(title = 'Wallet address')
  password: str = Field(title = 'Password')
  
class User(UserBase):
  id: int
  deleted: bool
  
  class Config:
    orm_mode = True