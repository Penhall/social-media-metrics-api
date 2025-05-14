import redis
from redis.exceptions import RedisError
from app.core.config import settings
import logging
from typing import Optional, Any, Callable, TypeVar, cast
import pickle
from functools import wraps

logger = logging.getLogger(__name__)
T = TypeVar('T')

class APICache:
    """Gerencia cache de respostas de API usando Redis"""
    
    def __init__(self):
        self.redis_client = redis.Redis.from_url(
            settings.REDIS_URL,
            decode_responses=False
        )
        
    def get(self, key: str) -> Optional[Any]:
        """Obtém valor do cache"""
        try:
            cached_data = self.redis_client.get(key)
            if cached_data:
                return pickle.loads(cached_data)
            return None
        except RedisError as e:
            logger.error(f"Erro ao acessar cache: {str(e)}")
            return None
            
    def set(self, key: str, value: Any, timeout: int = 3600) -> bool:
        """Armazena valor no cache com timeout em segundos"""
        try:
            serialized = pickle.dumps(value)
            return self.redis_client.setex(
                key,
                timeout,
                serialized
            )
        except RedisError as e:
            logger.error(f"Erro ao armazenar no cache: {str(e)}")
            return False
            
    def delete(self, key: str) -> bool:
        """Remove valor do cache"""
        try:
            return self.redis_client.delete(key) > 0
        except RedisError as e:
            logger.error(f"Erro ao remover do cache: {str(e)}")
            return False

    def cached(self, timeout: int = 3600, key_prefix: str = "cache_"):
        """Decorator para cache automático de resultados de função"""
        def decorator(func: Callable[..., T]) -> Callable[..., T]:
            @wraps(func)
            def wrapper(*args, **kwargs) -> T:
                cache_key = f"{key_prefix}{func.__name__}_{str(args)}_{str(kwargs)}"
                cached_value = self.get(cache_key)
                if cached_value is not None:
                    return cached_value
                
                result = func(*args, **kwargs)
                self.set(cache_key, result, timeout)
                return result
            return cast(Callable[..., T], wrapper)
        return decorator

# Instância global do cache
cache = APICache()