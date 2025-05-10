from app.db.database import engine
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        with engine.connect() as conn:
            logger.info("✅ Conexão com o banco de dados bem-sucedida!")
            return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    exit(0 if success else 1)