import httpx
from typing import Optional, Dict, Any
from fastapi import HTTPException

async def make_api_request(
    url: str,
    method: str = "GET",
    headers: Optional[Dict[str, str]] = None,
    params: Optional[Dict[str, Any]] = None,
    json: Optional[Dict[str, Any]] = None,
    timeout: int = 30
) -> Dict[str, Any]:
    """Faz requisições HTTP com tratamento de erros"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.request(
                method=method,
                url=url,
                headers=headers or {},
                params=params or {},
                json=json or {},
                timeout=timeout
            )
            response.raise_for_status()
            return response.json()
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"API request failed: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"API request error: {str(e)}"
        )

def build_query_params(params: Dict[str, Any]) -> Dict[str, Any]:
    """Remove parâmetros nulos/vazios para requisições API"""
    return {k: v for k, v in params.items() if v is not None and v != ""}