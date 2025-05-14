from pydantic import PostgresDsn, validator, Field, ValidationError
from pydantic_settings import BaseSettings
from typing import Any, Dict, Optional, Union

class Settings(BaseSettings):
    # Configurações do banco de dados
    # Tornar opcionais aqui, mas o validador garantirá que uma URI final seja definida
    POSTGRES_SERVER: Optional[str] = None
    POSTGRES_USER: Optional[str] = None
    POSTGRES_PASSWORD: Optional[str] = None
    POSTGRES_DB: Optional[str] = None
    DATABASE_URL: Optional[str] = None

    # Voltar para Optional = None. O validador abaixo garantirá que não permaneça None.
    SQLALCHEMY_DATABASE_URI: Optional[Union[PostgresDsn, str]] = None

    @validator("SQLALCHEMY_DATABASE_URI", pre=True, always=True)
    def assemble_db_connection(cls, v: Optional[Any], values: Any) -> Union[PostgresDsn, str]:
        # values é um objeto ValidationInfo em Pydantic v2
        raw_data = values.data if hasattr(values, 'data') else {}

        # Prioridade 1: Usar DATABASE_URL se fornecido no ambiente/env_file
        database_url_from_env = raw_data.get("DATABASE_URL")
        if database_url_from_env:
            # Verificar se é uma URL SQLite válida (simples verificação)
            if database_url_from_env.startswith("sqlite"):
                 return database_url_from_env
            # Tentar validar como PostgresDsn se não for SQLite
            try:
                # Tentar criar um PostgresDsn diretamente da URL
                # Isso valida o formato da URL PostgreSQL
                return PostgresDsn(database_url_from_env)
            except ValidationError as e:
                raise ValueError(f"Invalid DATABASE_URL format for PostgreSQL: {e}")

        # Prioridade 2: Usar SQLALCHEMY_DATABASE_URI se diretamente fornecido (v) - menos comum
        # Isso pode acontecer se o valor for passado diretamente ao criar Settings, não via env
        if isinstance(v, (str, PostgresDsn)):
             # Se for string, tentar validar como PostgresDsn se não for sqlite
             if isinstance(v, str) and not v.startswith("sqlite"):
                 try:
                     return PostgresDsn(v)
                 except ValidationError as e:
                     raise ValueError(f"Invalid SQLALCHEMY_DATABASE_URI format for PostgreSQL: {e}")
             return v # Retorna a string sqlite ou o PostgresDsn já validado


        # Prioridade 3: Tentar construir a partir dos componentes POSTGRES_*
        pg_user = raw_data.get("POSTGRES_USER")
        pg_password = raw_data.get("POSTGRES_PASSWORD")
        pg_server = raw_data.get("POSTGRES_SERVER")
        pg_db = raw_data.get("POSTGRES_DB")

        if pg_user and pg_server and pg_db:
            try:
                # Construir e validar como PostgresDsn
                return PostgresDsn.build(
                    scheme="postgresql",
                    username=pg_user,
                    password=pg_password,
                    host=pg_server,
                    path=pg_db
                )
            except ValidationError as e:
                 raise ValueError(f"Failed to build PostgresDsn from components: {e}")
            except Exception as e: # Capturar outros erros de build
                 raise ValueError(f"Error building PostgresDsn from components: {e}")

        # Se nenhuma configuração válida foi encontrada após todas as verificações
        raise ValueError("Database configuration is missing. Set DATABASE_URL or POSTGRES_USER/PASSWORD/SERVER/DB.")

    # Configurações de API (manter como antes)
    TWITTER_API_KEY: str
    TWITTER_API_SECRET: str
    FACEBOOK_APP_ID: str
    FACEBOOK_APP_SECRET: str
    INSTAGRAM_APP_ID: str
    INSTAGRAM_APP_SECRET: str
    WHATSAPP_BUSINESS_ID: str
    WHATSAPP_ACCESS_TOKEN: str

    # Configurações gerais (manter como antes)
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 8  # 8 dias
    BACKEND_CORS_ORIGINS: str = "*"
    ALGORITHM: str = "HS256" # Adicionar algoritmo JWT padrão se não existir

    class Config:
        case_sensitive = True
        # Remover env_file = ".env"
        extra = 'ignore'

settings = Settings()
