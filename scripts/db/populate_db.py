import sys
import logging
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from datetime import date
import psycopg2

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configuração do SQLAlchemy 2.0
Base = declarative_base()

# String de conexão hardcoded temporariamente
DATABASE_URL = "postgresql://postgres:abc123@localhost:5432/social_metrics"

def create_engine_with_encoding():
    """Cria engine com encoding explícito"""
    try:
        # Força encoding UTF-8 e timeout de conexão
        engine = create_engine(
            DATABASE_URL,
            connect_args={
                'options': '-c client_encoding=utf8',
                'connect_timeout': 10
            },
            pool_pre_ping=True
        )
        return engine
    except Exception as e:
        logger.error(f"Erro ao criar engine: {str(e)}")
        raise

def check_database_connection(engine):
    """Verifica conexão com o banco"""
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Falha na conexão: {str(e)}")
        return False

def populate_test_data():
    try:
        logger.info("Iniciando população de dados...")
        
        # Cria engine com encoding explícito
        engine = create_engine_with_encoding()
        
        if not check_database_connection(engine):
            raise ConnectionError("Não foi possível conectar ao banco")

        # Cria sessão
        Session = sessionmaker(bind=engine)
        session = Session()

        # Verifica se tabelas existem
        inspector = inspect(engine)
        required_tables = ["platforms", "metrics", "users"]
        
        for table in required_tables:
            if not inspector.has_table(table):
                raise RuntimeError(f"Tabela {table} não existe no banco")

        # Popula dados de teste (implementação existente)
        # ...

        session.commit()
        logger.info("✅ Dados populados com sucesso!")
        return True

    except Exception as e:
        logger.error(f"❌ Erro ao popular dados: {str(e)}")
        return False
    finally:
        if 'session' in locals():
            session.close()

if __name__ == "__main__":
    success = populate_test_data()
    sys.exit(0 if success else 1)