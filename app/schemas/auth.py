# app/schemas/auth.py

from pydantic import BaseModel, EmailStr

# Base schema for user-related attributes
class UserBase(BaseModel):
    """
    Base schema for user-related attributes, typically used for creating or logging in users.
    
    Attributes:
        username (str): The username of the user.
    """
    email: EmailStr

# Schema for user creation (includes email and password)
class UserCreate(UserBase):
    """
    Schema for user creation, including required email and password.
    
    Attributes:
        email (EmailStr): The user's email address.
        password (str): The user's password.
    """
    username: str
    password: str

# Schema for user login (includes username and password)
class UserLogin(UserBase):
    """
    Schema for user login, requiring the username and password.
    
    Attributes:
        password (str): The user's password.
    """
    password: str

class RegisterResponse(UserBase):
    username:str
    message: str



class LoginResponse(BaseModel):
    api_key:str
    token_type: str
    username:str

class DetailResponse(BaseModel):
    detail: str

class APIKeyResponse(BaseModel):
    detail: str
    api_key: str