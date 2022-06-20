from fastapi import APIRouter, status, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from operator import and_
from typing import Union, Any
from datetime import datetime
from jose import jwt
from pydantic import ValidationError

from utils import (
  ALGORITHM,
  JWT_SECRET_KEY
)
from utils import (
    get_hashed_password,
    create_access_token,
    create_refresh_token,
    verify_password
)
from schemas.user import EmailUserBase
from schemas.auth import TokenPayload, TokenSchema
from db.database import Database
from models.user import User


router = APIRouter(
  prefix='/auth',
  tags=['auth'],
  responses={404: {"description": "Not found"}},
)

email_oauth = OAuth2PasswordBearer(
  tokenUrl="auth/login/email",
  scheme_name="JWT"
)

database = Database()
engine = database.get_db_connection()

async def get_current_user(token: str = Depends(email_oauth)) -> User:
  try:
    payload = jwt.decode(
      token, JWT_SECRET_KEY, algorithms=[ALGORITHM]
    )
    token_data = TokenPayload(**payload)
    
    if datetime.fromtimestamp(token_data.exp) < datetime.now():
      raise HTTPException(
        status_code = status.HTTP_401_UNAUTHORIZED,
        detail="Token expired",
        headers={"WWW-Authenticate": "Bearer"},
      )
  except(jwt.JWTError, ValidationError):
    raise HTTPException(
      status_code=status.HTTP_403_FORBIDDEN,
      detail="Could not validate credentials",
      headers={"WWW-Authenticate": "Bearer"},
    )
  
  session = database.get_db_session(engine)
  user: User = session.query(User).filter(and_(token_data.sub == User.id, User.deleted == False)).one()
  
  if user is None:
    raise HTTPException(
      status_code=status.HTTP_404_NOT_FOUND,
      detail="Could not find user",
    )
  
  return user

@router.post('/signup/email', summary="Create new user",)
async def create_user_by_email(data: EmailUserBase):
  # querying database to check if user already exist
  session: Session = database.get_db_session(engine)
  user = session.query(User).filter(and_(User.email == data.email, User.deleted == False)).first()
  if user is not None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="User with this email already exist"
    )
  
  new_user = User()
  new_user.first_name = data.first_name
  new_user.last_name = data.last_name
  new_user.email = data.email
  new_user.hashed_password = get_hashed_password(data.password)
  
  session.add(new_user)
  session.flush()
  session.refresh(new_user, attribute_names=['id'])
  data = {'user_id': new_user.id}
  session.commit()
  session.close()
  return data

@router.post('/login/email', summary="Create access and refresh tokens for user", response_model=TokenSchema)
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
  session: Session = database.get_db_session(engine)
  user: User = session.query(User).filter(and_(User.email == form_data.username, User.deleted == False)).first()
  if user is None:
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorrect email or password"
    )

  if not verify_password(form_data.password, user.hashed_password):
    raise HTTPException(
      status_code=status.HTTP_400_BAD_REQUEST,
      detail="Incorrect email or password"
    )
  
  return {
    "access_token": create_access_token(user.id),
    "refresh_token": create_refresh_token(user.id),
  }