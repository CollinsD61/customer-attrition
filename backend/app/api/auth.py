import jwt
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer

from backend.app.core.security import (
    create_token,
    hash_password,
    verify_password,
    verify_token,
)
from backend.app.db.session import get_db
from backend.app.repositories.user_repository import UserRepository
from backend.app.schemas.auth import LoginRequest, TokenResponse, UserCreate

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def get_current_user(token: str = Depends(oauth2_scheme)) -> dict:
    try:
        payload = verify_token(token)
        return payload
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token"
        ) from None


@router.post("/login", response_model=TokenResponse)
def login(request: LoginRequest, db=Depends(get_db)):  # noqa: B008
    repo = UserRepository(db)
    user = repo.get_by_username(request.username)
    if user is None or not verify_password(request.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials"
        )
    token = create_token(user.username)
    return TokenResponse(access_token=token)


@router.post("/register", response_model=TokenResponse)
def register(request: UserCreate, db=Depends(get_db)):  # noqa: B008
    repo = UserRepository(db)
    if repo.get_by_username(request.username):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Username already exists"
        )
    if repo.get_by_email(request.email):
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail="Email already exists"
        )
    hashed = hash_password(request.password)
    user = repo.create_user(request.username, request.email, hashed)
    token = create_token(user.username)
    return TokenResponse(access_token=token)
