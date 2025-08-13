from fastapi import APIRouter, Depends, HTTPException, Response, Request
from database import get_db
from sqlalchemy.orm import Session
from models import User
from utils.hashing import (
    hash_password,
    verify_password,
    create_access_token
)
from schemas.user import UserCreate, UserRead, UserLogin, UserUpdate, UserLoginSuccess
from utils.user import allowed_role, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserRead)
def register_user(user: UserCreate, db: Session = Depends(get_db)):
    hashed_password = hash_password(user.password)
    new_user = User(email=user.email, password=hashed_password, name=user.name)
    db.add(new_user)
    db.commit()
    return new_user


@router.post("/login", response_model=UserLoginSuccess)
def login_user(user: UserLogin, response: Response, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user.email).first()

    if not existing_user:
        raise HTTPException(status_code=404, detail=f"Wrong email")

    if not verify_password(user.password, existing_user.password):
        raise HTTPException(status_code=404, detail="Wrong password")

    token, max_age = create_access_token(
        existing_user.email, existing_user.role.role_name
    )
    print(existing_user.role.role_name)

    response.set_cookie(key="access_token", value=token, httponly=True, max_age=max_age)

    return {
        "user": existing_user,
        "message": "Successfully Logged In",
        "access_token": token,
        "token_type": "bearer",
    }


@router.post("/logout", response_model=dict)
def logout_user(response: Response):
    response.delete_cookie("access_token")
    response.status_code = 200
    return response


@router.get("/me", response_model=UserRead)
def get_me(user: UserRead = Depends(get_current_user)):
    return user
