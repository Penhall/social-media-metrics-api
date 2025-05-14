from fastapi import APIRouter, Request, HTTPException
from fastapi.responses import JSONResponse
from app.core.config import settings
import hmac
import hashlib

router = APIRouter()

async def verify_webhook_signature(request: Request) -> Request:
    """Middleware para validação HMAC de webhooks"""
    signature = request.headers.get('X-Signature')
    if not signature:
        raise HTTPException(status_code=401, detail="Assinatura ausente")

    body = await request.body()
    secret = settings.WEBHOOK_SECRET.encode()
    
    # Suporta múltiplos algoritmos
    algo = request.headers.get('X-Signature-Algo', 'sha256')
    hash_algo = getattr(hashlib, algo, hashlib.sha256)
    
    expected_signature = hmac.new(secret, body, hash_algo).hexdigest()
    
    if not hmac.compare_digest(signature, expected_signature):
        raise HTTPException(status_code=401, detail="Assinatura inválida")
    
    # Injeta payload verificado no request
    request.state.verified_body = body
    return request

@router.post("/{platform}",
    summary="Recebe webhooks de plataformas sociais",
    description="""Endpoint para recebimento de webhooks com validação HMAC.
    
    **Headers obrigatórios:**
    - X-Signature: Assinatura HMAC do payload
    - X-Signature-Algo: Algoritmo usado (padrão: sha256)
    
    **Exemplo de chamada:**
    ```
    POST /webhooks/facebook
    Headers:
        X-Signature: abc123...
        X-Signature-Algo: sha256
    Body: { "event": "message", ... }
    ```
    """,
    responses={
        200: {"description": "Webhook processado com sucesso"},
        401: {"description": "Assinatura inválida"},
        400: {"description": "Plataforma não suportada"}
    }
)
async def handle_webhook(
    platform: str,
    request: Request = Depends(verify_webhook_signature)
):
    """Endpoint base para recebimento de webhooks"""
    body = request.state.verified_body
    
    # Validação básica de plataforma
    valid_platforms = ["facebook", "instagram", "twitter"]
    if platform not in valid_platforms:
        raise HTTPException(status_code=400, detail="Plataforma não suportada")
    
    # Obter payload bruto para validação
    body = await request.body()
    signature = request.headers.get("x-hub-signature")
    
    if platform == "facebook":
        if not signature or not verify_facebook_signature(
            body,
            signature,
            settings.FACEBOOK_APP_SECRET
        ):
            raise HTTPException(status_code=401, detail="Assinatura inválida")
    
    payload = await request.json()
    
    # Processar eventos do Facebook
    if platform == "facebook":
        if payload.get("object") == "page":
            from app.workers.tasks import process_facebook_event
            for entry in payload.get("entry", []):
                for event in entry.get("changes", []):
                    # Enfileirar evento para processamento assíncrono
                    process_facebook_event.delay(
                        event_type=event.get("field"),
                        event_data=event.get("value"),
                        page_id=entry.get("id")
                    )
    
    return JSONResponse(
        content={"status": "received", "platform": platform},
        status_code=200
    )