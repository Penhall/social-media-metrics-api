from typing import Optional
import os
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from cryptography.fernet import Fernet
from app.core.config import settings

# Configurações existentes
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Nova configuração AES
# A SECRET_KEY deve ser uma chave Fernet válida (bytes codificados em base64 url-safe)
# Se settings.SECRET_KEY é uma string (como lida do .env), ela já deve ser
# a representação string de uma chave Fernet. Precisamos codificá-la de volta para bytes.
try:
    # Assumindo que settings.SECRET_KEY é uma string base64-encoded (como Fernet.generate_key().decode())
    fernet_key_bytes = settings.SECRET_KEY.encode('utf-8')
    fernet = Fernet(fernet_key_bytes)
except Exception as e:
    # Isso pode acontecer se a SECRET_KEY não for uma chave Fernet válida.
    # Para desenvolvimento/teste, você pode querer gerar uma chave se não estiver definida ou for inválida,
    # mas em produção, uma chave inválida deve ser um erro fatal.
    print(f"AVISO: Falha ao inicializar Fernet com a SECRET_KEY fornecida: {e}. Verifique se é uma chave Fernet válida.")
    # Como fallback, para evitar que a aplicação quebre imediatamente durante o desenvolvimento/teste se a chave for ruim,
    # poderíamos gerar uma chave em tempo de execução, mas isso NÃO é seguro para produção.
    # print("AVISO: Gerando uma chave Fernet de fallback em tempo de execução. NÃO USE EM PRODUÇÃO.")
    # fernet_key_bytes = Fernet.generate_key()
    # fernet = Fernet(fernet_key_bytes)
    # print(f"Chave de fallback gerada (string): {fernet_key_bytes.decode()}")
    raise ValueError(f"A SECRET_KEY fornecida não é uma chave Fernet válida. Detalhes: {e}")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Se settings.ACCESS_TOKEN_EXPIRE_MINUTES não estiver definido em config.py, use um padrão.
        expire_minutes = getattr(settings, 'ACCESS_TOKEN_EXPIRE_MINUTES', 15)
        expire = datetime.utcnow() + timedelta(minutes=expire_minutes)
    to_encode.update({"exp": expire})
    
    # Para JWT, a chave pode ser uma string simples, não precisa ser uma chave Fernet.
    # No entanto, é comum usar a mesma SECRET_KEY se ela for suficientemente complexa.
    # Se ALGORITHM não estiver em settings, defina um padrão.
    algorithm = getattr(settings, 'ALGORITHM', 'HS256')
    encoded_jwt = jwt.encode(to_encode, settings.SECRET_KEY, algorithm=algorithm)
    return encoded_jwt

def encrypt_token(token: str) -> str:
    """Criptografa um token usando AES"""
    return fernet.encrypt(token.encode()).decode()

def decrypt_token(encrypted_token: str) -> str:
    """Descriptografa um token usando AES"""
    try:
        return fernet.decrypt(encrypted_token.encode()).decode()
    except Exception as e:
        # Em vez de um ValueError genérico, podemos ser mais específicos ou logar o erro.
        # from cryptography.fernet import InvalidToken
        # if isinstance(e, InvalidToken):
        #     raise ValueError("Token inválido ou expirado para decriptação.")
        raise ValueError(f"Falha na decriptação do token: {str(e)}")

def verify_token(token: str) -> bool:
    """Verifica se um token JWT é válido"""
    try:
        # Se ALGORITHM não estiver em settings, defina um padrão.
        algorithm = getattr(settings, 'ALGORITHM', 'HS256')
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[algorithm])
        return True
    except JWTError:
        return False
