import logging
from typing import Any, Dict, Optional
import requests
from pydantic import BaseModel, ValidationError
from app.core.config import settings
from app.utils.retry import retry
from app.utils.rate_limiter import RateLimiter

logger = logging.getLogger(__name__)

class SocialAPI:
    """Classe base para integração com APIs de redes sociais."""
    
    def __init__(self, api_name: str):
        self.api_name = api_name
        self.base_url = ""
        self.rate_limiter = RateLimiter(max_calls=5, period=1)
        self.session = requests.Session()
        
    @retry(max_retries=3, delay=1)
    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        headers: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Método genérico para fazer requisições HTTP."""
        url = f"{self.base_url}{endpoint}"
        
        with self.rate_limiter:
            try:
                response = self.session.request(
                    method=method,
                    url=url,
                    params=params,
                    json=data,
                    headers=headers,
                    timeout=10
                )
                response.raise_for_status()
                return response.json()
            except requests.exceptions.RequestException as e:
                self._handle_errors(e)
                raise
    
    def _handle_errors(self, error: Exception) -> None:
        """Tratamento padrão de erros para todas as APIs."""
        error_msg = f"Erro na API {self.api_name}: {str(error)}"
        logger.error(error_msg)
        
        if isinstance(error, requests.exceptions.HTTPError):
            if error.response.status_code == 401:
                logger.error("Erro de autenticação - verifique suas credenciais")
            elif error.response.status_code == 429:
                logger.error("Rate limit excedido - aguarde antes de tentar novamente")
    
    def validate_response(self, model: BaseModel, data: Dict[str, Any]) -> BaseModel:
        """Valida a resposta da API usando um modelo Pydantic."""
        try:
            return model(**data)
        except ValidationError as e:
            logger.error(f"Erro de validação na resposta da API {self.api_name}: {e}")
            raise