-- Criação do banco de dados social_metrics_db
CREATE DATABASE social_metrics_db
WITH
OWNER = postgres
ENCODING = 'UTF8'
LC_COLLATE = 'Portuguese_Brazil.1252'
LC_CTYPE = 'Portuguese_Brazil.1252'
TABLESPACE = pg_default
CONNECTION LIMIT = -1;

-- Comentário explicativo sobre o banco
COMMENT ON DATABASE social_metrics_db IS 'Banco de dados para armazenar métricas de redes sociais';