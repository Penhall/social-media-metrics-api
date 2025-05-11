from pydantic import BaseModel
from typing import Generic, TypeVar, Optional, List

T = TypeVar('T')

class BaseResponse(BaseModel):
    success: bool
    message: str

class DataResponse(BaseResponse, Generic[T]):
    data: Optional[T] = None

class ListResponse(BaseResponse, Generic[T]):
    data: List[T] = []
    total: int = 0
    page: int = 1
    limit: int = 10

class ErrorResponse(BaseResponse):
    error_code: str
    details: Optional[str] = None

class ValidationErrorItem(BaseModel):
    field: str
    message: str

class ValidationErrorResponse(BaseResponse):
    errors: List[ValidationErrorItem] = []