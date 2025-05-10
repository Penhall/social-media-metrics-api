import os
import logging
import psycopg2
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
from dotenv import load_dotenv
from urllib.parse import urlparse

# Configuração de logging colorido
logging.basicConfig(
    level=logging.INFO,
    format='\033[36m%(asctime)s - %(levelname)s - %(message)s\033[0m',
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Variável global para armazenar os parâmetros parseados da DATABASE_URL
PARSED_DB_PARAMS = {}

def configurar_ambiente():
    """Carrega variáveis de ambiente e parseia DATABASE_URL."""
    global PARSED_DB_PARAMS
    load_dotenv(override=True) # Força o recarregamento do .env
    
    db_url = os.getenv('DATABASE_URL')
    if not db_url:
        logger.error("DATABASE_URL não encontrada no .env. Verifique o arquivo.")
        return False

    try:
        parsed_url = urlparse(db_url)
        if not (parsed_url.username and parsed_url.hostname and parsed_url.port and parsed_url.path): # Senha pode ser vazia
            logger.error(f"DATABASE_URL está incompleta: {db_url}. Precisa de usuário, host, porta e nome do banco.")
            return False
        
        PARSED_DB_PARAMS['dbname'] = parsed_url.path.lstrip('/')
        PARSED_DB_PARAMS['user'] = parsed_url.username
        PARSED_DB_PARAMS['password'] = parsed_url.password or '' # Trata senha vazia
        PARSED_DB_PARAMS['host'] = parsed_url.hostname
        PARSED_DB_PARAMS['port'] = str(parsed_url.port)
        
        logger.info(f"DATABASE_URL parseada com sucesso: dbname='{PARSED_DB_PARAMS['dbname']}'")
        return True
    except Exception as e:
        logger.error(f"Erro ao parsear DATABASE_URL '{db_url}': {e}. Verifique o formato.")
        return False

def get_connection_params():
    """Retorna um dicionário com os parâmetros de conexão da DATABASE_URL parseada."""
    global PARSED_DB_PARAMS
    # Garante que configurar_ambiente foi chamado ou tem dados
    if not PARSED_DB_PARAMS and not configurar_ambiente():
        return {} # Retorna vazio se falhar
    return PARSED_DB_PARAMS

def testar_conexao_psycopg2():
    """Testa conexão direta usando psycopg2."""
    params = get_connection_params()
    if not all(params.get(k) is not None for k in ['user', 'host', 'port', 'dbname']): # password pode ser None/vazio
        logger.error(f"Parâmetros de conexão insuficientes para psycopg2: {params}")
        return False

    # Teste DSN k/v com dbname da DATABASE_URL (que agora deve ser social_metrics_db)
    # psycopg2.connect lida com password=None como string vazia se necessário.
    dsn_kv = f"dbname='{params['dbname']}' user='{params['user']}' password='{params['password']}' host='{params['host']}' port='{params['port']}' client_encoding='UTF8'"
    try:
        logger.info(f"Tentando psycopg2 com DSN k/v (dbname='{params['dbname']}'): dbname='{params['dbname']}' user='{params['user']}' password='********' host='{params['host']}' port='{params['port']}' client_encoding='UTF8'")
        conn = psycopg2.connect(dsn_kv)
        with conn.cursor() as cur:
            cur.execute("SELECT 1")
            if cur.fetchone()[0] == 1:
                logger.info(f"✅ Teste psycopg2 (DSN k/v, dbname='{params['dbname']}', UTF8): Conexão bem-sucedida!")
                conn.close()
                return True 
        conn.close()
    except Exception as e:
        logger.error(f"❌ Erro psycopg2 (DSN k/v, dbname='{params['dbname']}', UTF8): {str(e)}")
        return False

def testar_conexao_sqlalchemy():
    """Testa conexão usando SQLAlchemy."""
    db_url = os.getenv('DATABASE_URL') 
    if not db_url:
        logger.error("DATABASE_URL não definida para teste SQLAlchemy.")
        return False
    
    params = get_connection_params() 
    
    try:
        # Esconde a senha no log
        log_db_url = db_url
        if params.get('password'):
            log_db_url = db_url.replace(params['password'], '********', 1)
        logger.info(f"Tentando SQLAlchemy com DATABASE_URL: {log_db_url}")
        
        engine = create_engine(
            db_url, 
            pool_pre_ping=True,
            connect_args={'options': '-c client_encoding=utf8'}
        )
        with engine.connect() as conn:
            result = conn.execute(text("SELECT version()")) 
            logger.info(f"✅ Teste SQLAlchemy (DATABASE_URL): {result.scalar()}")
            return True
    except SQLAlchemyError as e:
        logger.error(f"❌ Erro SQLAlchemy (DATABASE_URL): {str(e)}")
        return False

def verificar_encoding_servidor():
    """Verifica a codificação do servidor de banco de dados."""
    db_url = os.getenv('DATABASE_URL')
    if not db_url: 
        logger.error("DATABASE_URL não definida para verificar encoding do servidor.")
        return False
    
    db_url_base = db_url.split('?')[0]
    params = get_connection_params()

    try:
        log_db_url_base = db_url_base
        if params.get('password'):
            log_db_url_base = db_url_base.replace(params['password'], '********', 1)
        logger.info(f"Verificando encoding do servidor com URL base: {log_db_url_base}")

        engine = create_engine(db_url_base) 
        with engine.connect() as conn:
            server_encoding = conn.execute(text("SHOW server_encoding;")).scalar()
            client_encoding_db = conn.execute(text("SHOW client_encoding;")).scalar()
            logger.info(f"🔍 Encoding do servidor (SHOW server_encoding): {server_encoding}")
            logger.info(f"🔍 Encoding do cliente conectado (SHOW client_encoding): {client_encoding_db}")
            
            if server_encoding.lower() != 'utf8':
                 logger.warning(f"⚠️  O servidor PostgreSQL não está configurado para UTF8 (está {server_encoding}). Isso pode causar problemas de compatibilidade.")
            return server_encoding.lower() == 'utf8'
    except SQLAlchemyError as e:
        logger.error(f"❌ Erro ao verificar encoding do servidor: {str(e)}")
        return False

if __name__ == "__main__":
    if not configurar_ambiente(): # configurar_ambiente agora popula PARSED_DB_PARAMS
        exit(1)
        
    psycopg2_ok = testar_conexao_psycopg2()
    sqlalchemy_ok = False
    server_encoding_is_utf8 = False

    if psycopg2_ok: 
        sqlalchemy_ok = testar_conexao_sqlalchemy()
        if sqlalchemy_ok:
            server_encoding_is_utf8 = verificar_encoding_servidor()
    
    if psycopg2_ok and sqlalchemy_ok:
        logger.info("🎉 Testes de conexão psycopg2 e SQLAlchemy passaram com sucesso!")
        if not server_encoding_is_utf8:
            logger.warning("⚠️  Atenção: O encoding do servidor PostgreSQL não é UTF8. Recomenda-se alterá-lo para UTF8 para evitar problemas futuros com caracteres especiais.")
        exit(0)
    else:
        logger.error("🔥 Problemas de conexão encontrados:")
        if not psycopg2_ok:
            logger.error("  - Falha na conexão com psycopg2.")
        elif not sqlalchemy_ok: 
            logger.error("  - Falha na conexão com SQLAlchemy.")
        
        if not server_encoding_is_utf8 and (psycopg2_ok and sqlalchemy_ok):
             pass 
        elif not server_encoding_is_utf8 : 
             logger.info("  - Informação adicional: A verificação do encoding do servidor falhou ou o servidor não é UTF8.")
        exit(1)
