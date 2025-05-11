from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import User
from app.schemas.user import UserCreate
from app.services.user_service import create_user, get_user_by_id

router = APIRouter()

@router.post("/users", response_model=User, status_code=201)
async def create_new_user(user: UserCreate, db: Session = Depends(get_db)):
    """
    Cria um novo usuário no sistema
    """
    try:
        return create_user(db=db, user=user)
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Erro ao criar usuário: {str(e)}"
        )

@router.get("/users/{user_id}", response_model=User)
async def read_user(user_id: int, db: Session = Depends(get_db)):
    """
    Busca um usuário pelo ID
    """
    db_user = get_user_by_id(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="Usuário não encontrado")
    return db_user