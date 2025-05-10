from sqlalchemy.orm import Session
from . import models

# Operações CRUD para Platform
def create_platform(db: Session, name: str, url: str = None):
    db_platform = models.Platform(name=name, url=url)
    db.add(db_platform)
    db.commit()
    db.refresh(db_platform)
    return db_platform

def get_platform(db: Session, platform_id: int):
    return db.query(models.Platform).filter(models.Platform.id == platform_id).first()

def get_platforms(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Platform).offset(skip).limit(limit).all()

def update_platform(db: Session, platform_id: int, name: str = None, url: str = None):
    db_platform = get_platform(db, platform_id)
    if db_platform:
        if name:
            db_platform.name = name
        if url:
            db_platform.url = url
        db.commit()
        db.refresh(db_platform)
    return db_platform

def delete_platform(db: Session, platform_id: int):
    db_platform = get_platform(db, platform_id)
    if db_platform:
        db.delete(db_platform)
        db.commit()
    return db_platform

# Operações CRUD para Metric
def create_metric(db: Session, platform_id: int, metric_name: str, value: float, date: str):
    db_metric = models.Metric(
        platform_id=platform_id,
        metric_name=metric_name,
        value=value,
        date=date
    )
    db.add(db_metric)
    db.commit()
    db.refresh(db_metric)
    return db_metric

def get_metric(db: Session, metric_id: int):
    return db.query(models.Metric).filter(models.Metric.id == metric_id).first()

def get_metrics_by_platform(db: Session, platform_id: int, skip: int = 0, limit: int = 100):
    return db.query(models.Metric).filter(models.Metric.platform_id == platform_id).offset(skip).limit(limit).all()

def update_metric(db: Session, metric_id: int, value: float = None):
    db_metric = get_metric(db, metric_id)
    if db_metric and value:
        db_metric.value = value
        db.commit()
        db.refresh(db_metric)
    return db_metric

def delete_metric(db: Session, metric_id: int):
    db_metric = get_metric(db, metric_id)
    if db_metric:
        db.delete(db_metric)
        db.commit()
    return db_metric

# Operações CRUD para User
def create_user(db: Session, username: str, email: str, hashed_password: str):
    db_user = models.User(
        username=username,
        email=email,
        hashed_password=hashed_password
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()

def update_user(db: Session, user_id: int, username: str = None, email: str = None, is_active: bool = None):
    db_user = get_user(db, user_id)
    if db_user:
        if username:
            db_user.username = username
        if email:
            db_user.email = email
        if is_active is not None:
            db_user.is_active = is_active
        db.commit()
        db.refresh(db_user)
    return db_user

def delete_user(db: Session, user_id: int):
    db_user = get_user(db, user_id)
    if db_user:
        db.delete(db_user)
        db.commit()
    return db_user