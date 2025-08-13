from models import Role, User
from fastapi import Depends, APIRouter, HTTPException, status
from database import get_db
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from utils.user import allowed_role
from typing import List, Dict
from schemas.role import RoleCreate, RoleRead, RoleUpdate
from schemas.user import UserRead

router = APIRouter(prefix="/roles", tags=["roles"])


@router.get("/", response_model=List[RoleRead])
def get_roles(
    current_user: User = Depends(allowed_role("admin")), db: Session = Depends(get_db)
):
    roles = db.query(Role).all()
    return roles


@router.post("/", response_model=RoleRead)
def create_role(
    role: RoleCreate,
    current_user: User = Depends(allowed_role("admin")),
    db: Session = Depends(get_db),
):
    existing_role = db.query(Role).filter(Role.role_name == role.role_name).first()
    if existing_role:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role '{role.role_name}' already exists.",
        )

    new_role = Role(role_name=role.role_name)
    db.add(new_role)

    db.commit()
    db.refresh(new_role)
    return new_role


@router.delete("/{role_id}", response_model=Dict[str, str])
def delete_role(
    role_id: int,
    current_user=Depends(allowed_role("admin")),
    db: Session = Depends(get_db),
):
    role = db.query(Role).filter(Role.id == role_id).first()
    if not role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role with the id: {role_id} doesn't exist.",
        )
    try:
        db.delete(role)
        db.commit()
        return {"message": f"Role: {role_id} successfully deleted"}
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Role is assigned to a users, cannot delete.",
        )


@router.patch("/{role_id}", response_model=RoleRead)
def update_role(
    role_id: int,
    role: RoleUpdate,
    current_user=Depends(allowed_role("admin")),
    db: Session = Depends(get_db),
):
    existing_role = db.query(Role).filter(Role.id == role_id).first()
    if not existing_role:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Role id: '{role_id}' doesn't exist.",
        )
    if role.role_name is not None:
        existing_role.role_name = role.role_name

    try:
        db.commit()
        db.refresh(existing_role)
        return existing_role
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Role name '{role.role_name}' already exists.",
        )


@router.post("/{role_id}/assign", response_model=UserRead)
def assign_role_to_user(
    role_id: int,
    user_id: int,
    current_user=Depends(allowed_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User doesn't exist."
        )

    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot assign role to yourself.",
        )

    user.role_id = role_id
    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role doesn't exist"
        )


@router.post("/{role_id}/revoke", response_model=UserRead)
def revoke_role_from_user(
    role_id: int,
    user_id: int,
    current_user=Depends(allowed_role("admin")),
    db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=f"User doesn't exist."
        )

    if current_user.id == user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You cannot revoke a role from yourself.",
        )

    if user.role_id == role_id:
        user.role_id = 5

    try:
        db.commit()
        db.refresh(user)
        return user
    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"Role doesn't exist"
        )
