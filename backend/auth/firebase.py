from fastapi import HTTPException, status
import requests
from google.auth.transport import requests as google_requests
from google.oauth2 import id_token
from jose import jwt
import json

from config import settings
from models import User, UserRole

# Firebase Authentication
def verify_firebase_token(token: str):
    """
    Verify Firebase ID token and return the user information.
    """
    try:
        # For web clients, we can verify the token using Google's auth library
        firebase_cert_url = f"https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com"
        
        # Verify the token against Firebase Auth
        headers = {'User-Agent': 'TelecomApp/1.0'}
        auth_url = f"https://identitytoolkit.googleapis.com/v1/accounts:lookup?key={settings.FIREBASE_API_KEY}"
        
        # First, verify the token with Firebase
        payload = json.dumps({"idToken": token})
        response = requests.post(
            auth_url,
            headers={
                'Content-Type': 'application/json',
                **headers
            },
            data=payload
        )
        
        if response.status_code != 200:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid Firebase token",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        firebase_user = response.json().get("users", [{}])[0]
        
        return {
            "email": firebase_user.get("email"),
            "email_verified": firebase_user.get("emailVerified", False),
            "name": firebase_user.get("displayName", ""),
            "firebase_uid": firebase_user.get("localId")
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Failed to authenticate with Firebase: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_or_create_user_from_firebase(db, firebase_user_info, role=None):
    """
    Get existing user or create a new one based on Firebase auth info.
    """
    if not firebase_user_info.get("email"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email not found in Firebase token",
        )
    
    # Check if user exists, create if not
    user = db.query(User).filter(User.email == firebase_user_info["email"]).first()
    if not user:
        user = User(
            email=firebase_user_info["email"],
            full_name=firebase_user_info.get("name", ""),
            firebase_uid=firebase_user_info.get("firebase_uid"),
            is_firebase_auth=True,
            role=role if role else UserRole.OPERATIVO  # Use provided role or default to NOC
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    elif not user.firebase_uid:
        # Update existing user with Firebase UID if not set
        user.firebase_uid = firebase_user_info.get("firebase_uid")
        user.is_firebase_auth = True
        # Update role if provided and user is new to Firebase auth
        if role:
            user.role = role
        db.commit()
        db.refresh(user)
        
    return user