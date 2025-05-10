import psycopg2
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
        
        conn = psycopg2.connect(
            db_url,
            options="-c client_encoding=utf8"
        )
        conn.set_client_encoding('UTF8')
        
        with conn.cursor() as cur:
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logger.info(f"Encoding do cliente: {encoding}")
            
        logger.info("✅ Conexão direta com psycopg2 bem-sucedida!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()