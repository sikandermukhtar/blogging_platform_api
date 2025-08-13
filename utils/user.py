from fastapi import Request, Depends, HTTPException, status
from sqlalchemy.orm import Session
from models import User
from database import get_db
from fastapi.security import OAuth2PasswordBearer
from .hashing import decode_access_token
from typing import List, Optional

oauth_scheme = OAuth2PasswordBearer(tokenUrl="")


def get_current_user(
    request: Request, token: str = Depends(oauth_scheme), db: Session = Depends(get_db)
):
    cookie_token = request.cookies.get("access_token")
    if cookie_token:
        token = cookie_token

    payload = decode_access_token(token)

    email = payload["email"]

    user = db.query(User).filter(User.email == email).first()
    if not user:
        raise HTTPException(status_code=404, detail="No user found!")

    return user


def allowed_role(*allowed_role: str):
    async def role_checking(current_user=Depends(get_current_user)):
        if current_user.role.role_name not in allowed_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN, detail="Not enough permissions"
            )
        return current_user

    return role_checking


def allow_blog_owner_or_roles(
    get_resource_function,
    owner_attribute: str = "owner_id",
    allowed_roles: Optional[List[str]] = None,
):
    allowed_roles = allowed_roles or []

    def inner_dependency_function(
        blog_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        resource = get_resource_function(blog_id, db)

        if resource is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found."
            )

        owner_id = getattr(resource, owner_attribute)
        if owner_id == current_user.id:
            return resource
        if current_user.role in allowed_roles:
            return resource

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the action.",
        )

    return inner_dependency_function


def allow_comment_owner_or_roles(
    get_resource_function,
    owner_attribute: str = "owner_id",
    allowed_roles: Optional[List[str]] = None,
):
    allowed_roles = allowed_roles or []

    def inner_dependency_function(
        comment_id: int,
        db: Session = Depends(get_db),
        current_user=Depends(get_current_user),
    ):
        resource = get_resource_function(comment_id, db)

        if resource is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, detail="Resource not found."
            )

        owner_id = getattr(resource, owner_attribute)
        if owner_id == current_user.id:
            return resource
        if current_user.role in allowed_roles:
            return resource

        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Not authorized to perform the action.",
        )

    return inner_dependency_function
