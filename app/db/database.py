from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
# Remover import os e load_dotenv, pois as configurações virão de app.core.config
from app.core.config import settings # Importar as configurações centralizadas

# Usar a URI do banco de dados das configurações
# settings.SQLALCHEMY_DATABASE_URI já lida com a lógica de DATABASE_URL ou POSTGRES_*
# e já é uma string ou PostgresDsn. create_engine pode lidar com ambos.
db_url = str(settings.SQLALCHEMY_DATABASE_URI) # Garantir que seja uma string

engine_args = {}
if not db_url.startswith("sqlite"):
    engine_args.update({
        "pool_pre_ping": True,
        "pool_size": 10,
        "max_overflow": 20,
        "connect_args": {'options': '-c client_encoding=utf8'}
    })
# Para SQLite, connect_args={"check_same_thread": False} é comum,
# mas isso já é tratado no conftest.py para a engine de teste.
# Para a engine principal, se for SQLite, não precisa de connect_args especiais aqui
# a menos que haja um requisito específico.
# Se a aplicação principal também puder usar SQLite e precisar de check_same_thread=False,
# essa lógica precisaria ser adicionada aqui também.
# Por enquanto, vamos manter simples e focar nos argumentos que causam erro.
elif db_url.startswith("sqlite"):
    # Para SQLite, é comum precisar de check_same_thread=False se usado em múltiplos threads,
    # o que pode acontecer com FastAPI.
    engine_args["connect_args"] = {"check_same_thread": False}


engine = create_engine(db_url, **engine_args)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
