from sqlalchemy.orm import Session
from fastapi import HTTPException

from app.db.models import User
from app.schemas.user import UserCreate
from app.core.security import get_password_hash

def create_user(db: Session, user: UserCreate) -> User:
    # Verifica se usuário já existe
    db_user = db.query(User).filter(
        (User.email == user.email) | 
        (User.username == user.username)
    ).first()
    
    if db_user:
        raise HTTPException(
            status_code=400,
            detail="Email ou username já cadastrado"
        )

    # Cria novo usuário
    hashed_password = get_password_hash(user.password)
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password
    )
    
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user_by_id(db: Session, user_id: int) -> User:
    """Busca um usuário pelo ID"""
    db_user = db.query(User).filter(User.id == user_id).first()
    return db_user