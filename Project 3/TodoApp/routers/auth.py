from datetime import timedelta, datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Users
from passlib.context import CryptContext
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from jose import jwt, JWTError

# auth.py is created to keep authentication code separately to keep things more organised

# Create a router for authentication endpoints
router = APIRouter(
    prefix='/auth',
    tags=['auth']
)
# each API endpoint will start with 'auth'

# Secret key and algorithm for JWT
SECRET_KEY = '197b2c37c391bed93fe80344fe73b806947a65e36206e05a1a23c2fa12702fe3'
ALGORITHM = 'HS256'
# work together to add a signature to the JWT
bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')
oauth2_bearer = OAuth2PasswordBearer(tokenUrl='auth/token') # Token URL for OAuth2 password bearer
# oauth2_bearer is a dependency function that takes no arguments and returns a value (in this case, a JWT token).

# Pydantic model for creating a user
class CreateUserRequest(BaseModel):
    username: str
    email: str
    first_name: str
    last_name: str
    password: str
    role: str

# Pydantic model for the token response
class Token(BaseModel):
    access_token: str
    token_type: str

# Dependency function to get a database session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Dependency for a database session
db_dependency = Annotated[Session, Depends(get_db)]

# Function to authenticate a user
def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user: # user not registered 
        return False
    if not bcrypt_context.verify(password, user.hashed_password): # password does not match
        return False
    return user

# Function to create an access token using JWT
def create_access_token(username: str, user_id: int, role: str, expires_delta: timedelta):
    encode = {'sub': username, 'id': user_id, 'role': role}
    expires = datetime.now(timezone.utc) + expires_delta # expiration is critical for security reasons, eg 1h
    encode.update({'exp': expires})
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)
# Very fast for the server to discover if JWT was altered

# JWT: Json Web Token: extremely popular, authorisation method (including microservices)
# Header + Payload + Signature (aaa.bbb.ccc)
# Header: algorithm for signing + specific type of token
# Payload: data about subject
# Signature: apply the header algo to hash header and payload (signature saved on server)

# Dependency function to get the current user from the token
async def get_current_user(token: Annotated[str, Depends(oauth2_bearer)]):
    # Annotated[str, Depends(oauth2_bearer)]: This uses the Annotated type from Python's typing module to provide additional information about the parameter.
    # Depends(oauth2_bearer): The Depends function is used to specify that the token parameter should be provided by the oauth2_bearer dependency. 
    # The oauth2_bearer is an instance of OAuth2PasswordBearer that handles the extraction of the JWT token from the request headers.
    # Injection:
    # - When a route handler or another dependency function is called, FastAPI automatically detects the Depends(oauth2_bearer) annotation.
    # - It calls the oauth2_bearer function to obtain the dependency value and injects it into the route handler as a parameter.
    # Error Handling:
    # - If the oauth2_bearer function raises an exception (e.g., due to an invalid token), FastAPI will catch the exception and return an appropriate HTTP response.
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get('sub') # sub is the username
        user_id: int = payload.get('id')
        user_role: str = payload.get('role')
        if username is None or user_id is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                                detail='Could not validate user.')
        return {'username': username, 'id': user_id, 'user_role': user_role}
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')

# Endpoint to create a new user
@router.post("/", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency,
                      create_user_request: CreateUserRequest):
    create_user_model = Users(
        email=create_user_request.email,
        username=create_user_request.username,
        first_name=create_user_request.first_name,
        last_name=create_user_request.last_name,
        role=create_user_request.role,
        hashed_password=bcrypt_context.hash(create_user_request.password),
        is_active=True
    )
    # We need to add one line per item because we need to convert the password to a hashed password
    # We cannot use **...model_dump inside create_user_request

    db.add(create_user_model) # add new user to the database
    db.commit()
    
# Endpoint to get access token
@router.post("/token", response_model=Token)
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
                                 db: db_dependency):
    # OAuth2PasswordRequestForm: The type of the parameter is OAuth2PasswordRequestForm, which is a Pydantic model designed to validate and parse data from an OAuth2 password request form. 
    # This typically includes the username and password.
    # Depends(): The Depends function is used to specify that the form_data parameter should be provided by the OAuth2PasswordRequestForm dependency. 
    # The OAuth2PasswordRequestForm is an instance of OAuth2PasswordRequestForm that handles parsing the form data from the request.
    # db_dependency: This is a dependency that provides a database session. 
    # The db_dependency is an instance of Annotated[Session, Depends(get_db)], which means it will use the get_db dependency to provide a database session.
    user = authenticate_user(form_data.username, form_data.password, db) # username and password provided by user
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED,
                            detail='Could not validate user.')
    token = create_access_token(user.username, user.id, user.role, timedelta(minutes=20))

    return {'access_token': token, 'token_type': 'bearer'}







