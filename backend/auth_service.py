
import jwt
import datetime
from fastapi import HTTPException, Security, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from passlib.context import CryptContext
from typing import Optional

# --- CONFIG ---
SECRET_KEY = "IITU_SUPER_SECRET_KEY_CHANGE_IN_PROD"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60 * 24  # 1 day session

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")
security = HTTPBearer()

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[datetime.timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.datetime.utcnow() + expires_delta
    else:
        expire = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def decode_token(token: str):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        return None
    except jwt.InvalidTokenError:
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = Security(security)):
    token = credentials.credentials
    payload = decode_token(token)
    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return payload

def get_optional_user(request: Request):
    """
    Returns user payload if authenticated, else None.
    Does NOT raise 401.
    """
    auth_header = request.headers.get("Authorization")
    if not auth_header or not auth_header.startswith("Bearer "):
        return None
    
    token = auth_header.split(" ")[1]
    return decode_token(token)

def require_role(role: str):
    def role_checker(user: dict = Security(get_current_user)):
        if user["role"] != role and user["role"] != "admin": # Admin can do anything
            raise HTTPException(status_code=403, detail="Operation not permitted")
        return user
    return role_checker

# --- RELATIONAL PERSISTENCE (SQLite) ---
from teacher_assistant.src.infrastructure.relational_db import RelationalDatabase

db = RelationalDatabase()

def init_auth_db():
    """Bootstraps the auth database with default admin if empty."""
    if not db.get_user("admin@iitu.kz"):
        db.create_user(
            email="admin@iitu.kz", 
            password_hash=get_password_hash("admin123"),
            name="Super Admin",
            role="admin"
        )

# Initialize on module load (or call from main)
init_auth_db()

# Wrapper methods for the API to use
def get_user_by_email(email: str):
    return db.get_user(email)

def create_user(email, password, name, role):
    return db.create_user(
        email=email,
        password_hash=get_password_hash(password),
        name=name,
        role=role
    )

def list_all_users():
    return db.list_users()

def delete_user_by_email(email):
    db.delete_user(email)

