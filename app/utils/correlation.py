import uuid
from contextvars import ContextVar
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

correlation_id_var = ContextVar("correlation_id", default=None)

def generate_correlation_id() -> str:
    """Generate a new correlation ID using UUID4"""
    return str(uuid.uuid4())

class CorrelationIdMiddleware(BaseHTTPMiddleware):
    """Middleware to handle correlation IDs for request tracking"""
    
    async def dispatch(self, request: Request, call_next):
        # Get or generate correlation ID
        correlation_id = request.headers.get('X-Correlation-ID') or generate_correlation_id()
        correlation_id_var.set(correlation_id)
        
        # Process request
        response = await call_next(request)
        
        # Add correlation ID to response headers
        response.headers['X-Correlation-ID'] = correlation_id
        return response

def get_current_correlation_id() -> str:
    """Get the current correlation ID from context"""
    return correlation_id_var.get()