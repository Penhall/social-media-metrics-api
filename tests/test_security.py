import pytest
from app.core.security import (
    encrypt_token,
    decrypt_token,
    verify_token,
    create_access_token
)

def test_encrypt_decrypt_cycle():
    """Testa se a criptografia e descriptografia funcionam corretamente"""
    original_token = "test_token_123"
    encrypted = encrypt_token(original_token)
    decrypted = decrypt_token(encrypted)
    assert decrypted == original_token

def test_decrypt_invalid_token():
    """Testa falha ao descriptografar token inválido"""
    with pytest.raises(ValueError):
        decrypt_token("invalid_encrypted_token")

def test_verify_valid_token():
    """Testa verificação de token válido"""
    token = create_access_token({"sub": "test"})
    encrypted = encrypt_token(token)
    decrypted = decrypt_token(encrypted)
    assert verify_token(decrypted) is True

def test_verify_invalid_token():
    """Testa verificação de token inválido"""
    assert verify_token("invalid_token") is False

def test_verify_expired_token():
    """Testa verificação de token expirado"""
    from datetime import datetime, timedelta
    from app.core.config import settings
    from jose import jwt
    
    expired_token = jwt.encode(
        {"sub": "test", "exp": datetime.utcnow() - timedelta(minutes=1)},
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM
    )
    assert verify_token(expired_token) is False