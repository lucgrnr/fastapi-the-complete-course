from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

SQLALCHEMY_DATABASE_URL = 'mysql+pymysql://root:password@127.0.0.1:3306/TodoApplicationDatabase'
# database will be inside the directory of our app

engine = create_engine(SQLALCHEMY_DATABASE_URL)
# connection to database. By default SQllite only allows 1 thread to connect with it to prevent accidents.
# But with FastAPI, can be normal to have multiple accesss.

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()
# object to control the database

"""
SQLAlchemy is Python's most widely used SQL toolkit and Object-Relational Mapper (ORM), 
allowing you to interact with databases using Python objects and type-safe queries rather than raw SQL strings.
"""
# SQLite code: 
# SQLALCHEMY_DATABASE_URL = 'sqlite:///./todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={'check_same_thread': False}) 
# todosapp.db is the local database

# Postgress:
# SQLALCHEMY_DATABASE_URL = 'postgresql://postgres@localhost/TodoApplicationDatabase' #'sqlite:///./todosapp.db'
# engine = create_engine(SQLALCHEMY_DATABASE_URL)