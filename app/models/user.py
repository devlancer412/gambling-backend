from sqlalchemy import Column, Integer, String, TIMESTAMP, BOOLEAN, text
from db.database import Base

class User(Base):
  __tablename__ = "user"
  id = Column(Integer, primary_key=True)
  first_name = Column(String(512), nullable=False)
  last_name = Column(String(512), nullable=False)
  email = Column(String(512), nullable=True)
  wallet = Column(String(64), nullable=True)
  hashed_password = Column(String(512), nullable=False)
  deleted = (Column(BOOLEAN, default=False))
  created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
  updated_at = Column(TIMESTAMP, nullable=True, server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP"))