from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.exceptions import ValidationException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from pydantic import BaseModel
import requests
from models import Role
from config import settings
from db.database import get_db
from models import User, UserRole
from .utils import verify_password, get_password_hash, create_access_token, get_current_user
from .firebase import verify_firebase_token, get_or_create_user_from_firebase
from services.auth_service import  AuthService
router = APIRouter()

class TokenData(BaseModel):
    email: Optional[str] = None

class Token(BaseModel):
    access_token: str
    token_type: str
    user: dict

class UserCreate(BaseModel):
    email: str
    password: str
    full_name: str
    role: UserRole #= UserRole#.OPERATIVO

class UserReturn(BaseModel):
    id: str
    email: str
    full_name: str
    role: Optional[str] = None

class UserLogin(BaseModel):
    email: str
    password: str

class GoogleAuthRequest(BaseModel):
    token: str
    
class FirebaseAuthRequest(BaseModel):
    token: str
    role: Optional[UserRole] = None

@router.post("/register", response_model=UserReturn)
async def register_user(user_data: UserCreate, db: Session = Depends(get_db)):

    service = AuthService(db)
    print(user_data)
    try:
        #user_dict = user_data.model_dump()
        #print(user_dict)
        db_user = service.register_user(user_data)
        return {
            "id": str(db_user.id),
            "email": db_user.email,
            "full_name": db_user.full_name,
            "role": db_user.role.name}

    except ValidationException as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"Internal server error: {str(e)}")


@router.post("/login", response_model=Token)
async def login_for_access_token(user_data: UserLogin, db: Session = Depends(get_db)):
    # Authenticate user
    user = db.query(User).filter(User.email == user_data.email).first()
    if not user or not verify_password(user_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create access token
    access_token = create_access_token(
        data={"sub": user.email}
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": str(user.id),
            "email": user.email,
            "full_name": user.full_name,
            "role_id": str(user.role_id) if user.role_id else None
        }
    }

@router.post("/google", response_model=Token)
async def login_with_google(google_data: GoogleAuthRequest, db: Session = Depends(get_db)):
    # Verify Google token
    try:
        google_response = requests.get(
            f"https://www.googleapis.com/oauth2/v3/tokeninfo?id_token={google_data.token}"
        )
        if google_response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Google token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        google_info = google_response.json()
        email = google_info.get("email")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email not found in Google token",
            )
        
        # Check if user exists, create if not
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(
                email=email,
                full_name=google_info.get("name", ""),
                is_google_auth=True,
                role=UserRole.OPERATIVO  # Default role
            )
            db.add(user)
            db.commit()
            db.refresh(user)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": str(user.role)
            }
        }
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to authenticate with Google: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.post("/firebase", response_model=Token)
async def login_with_firebase(firebase_data: FirebaseAuthRequest, db: Session = Depends(get_db)):
    try:
        # Verify Firebase token
        firebase_user_info = verify_firebase_token(firebase_data.token)
        
        # Get or create user from Firebase info, using provided role if available
        user = get_or_create_user_from_firebase(db, firebase_user_info, role=firebase_data.role)
        
        # Create access token
        access_token = create_access_token(
            data={"sub": user.email}
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": str(user.role)
            }
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to authenticate with Firebase: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

@router.get("/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return {
        "id": str(current_user.id),
        "email": current_user.email,
        "full_name": current_user.full_name,
        "role_id": str(current_user.role_id) if current_user.role_id else None
    }
