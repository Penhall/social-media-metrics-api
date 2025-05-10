import psycopg2
from psycopg2 import sql
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def create_database():
    try:
        # Conecta ao banco template1 para criar o novo banco
        conn = psycopg2.connect(
            dbname="template1",
            user="postgres",
            password="abc123",
            host="localhost",
            port="5432"
        )
        conn.autocommit = True
        cursor = conn.cursor()
        
        logger.info("Criando banco de dados social_metrics_db...")
        
        # Executa o script SQL
        cursor.execute("""
            CREATE DATABASE social_metrics_db
            WITH
            OWNER = postgres
            ENCODING = 'UTF8'
            LC_COLLATE = 'Portuguese_Brazil.1252'
            LC_CTYPE = 'Portuguese_Brazil.1252'
            TABLESPACE = pg_default
            CONNECTION LIMIT = -1;
        """)
        
        cursor.execute("""
            COMMENT ON DATABASE social_metrics_db 
            IS 'Banco de dados para armazenar métricas de redes sociais';
        """)
        
        logger.info("✅ Banco criado com sucesso!")
        return True
        
    except psycopg2.Error as e:
        logger.error(f"Erro ao criar banco: {e}")
        return False
    finally:
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    success = create_database()
    exit(0 if success else 1)