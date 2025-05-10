import psycopg2
import logging
from urllib.parse import quote_plus

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_connection():
    try:
        # Codificar manualmente a senha
        password = quote_plus("abc123")
        db_url = f"postgresql://postgres:{password}@localhost:5432/social_metrics"
        
        logger.info(f"Tentando conectar com URL codificada: {db_url}")
        
        conn = psycopg2.connect(db_url)
        conn.set_client_encoding('UTF8')
        
        with conn.cursor() as cur:
            cur.execute("SHOW client_encoding;")
            encoding = cur.fetchone()[0]
            logger.info(f"Encoding do cliente: {encoding}")
            
        logger.info("✅ Conexão com URL codificada bem-sucedida!")
        return True
    except Exception as e:
        logger.error(f"❌ Erro na conexão: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection()