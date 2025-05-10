from sqlalchemy import create_engine
import os
import logging
from dotenv import load_dotenv

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

def test_connection():
    try:
        db_url = os.getenv('DATABASE_URL')
        logger.info(f"Tentando conectar com URL: {db_url}")
        
        engine = create_engine(
            db_url,
            connect_args={
                'options': '-c client_encoding=utf8'
            },
            echo=True
        )
        with engine.connect() as conn:
            print("✅ Conexão SQLAlchemy bem-sucedida!")
            return True
    except Exception as e:
        print(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()