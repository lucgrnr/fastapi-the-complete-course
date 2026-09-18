from database import Base
from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
# columns types


class Users(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True)
    username = Column(String, unique=True)
    first_name = Column(String)
    last_name = Column(String)
    hashed_password = Column(String) # cannot dehash, but same password leads to same hash, so we can check for matching passwords
    is_active = Column(Boolean, default=True)
    role = Column(String) # useful to allow admins to access information


class Todos(Base): # inherits Base from database.py
    __tablename__ = 'todos'

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)
    owner_id = Column(Integer, ForeignKey("users.id"))
    # last line to match users with their todo items