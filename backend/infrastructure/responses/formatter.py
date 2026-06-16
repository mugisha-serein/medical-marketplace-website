"""Unified response formatting for all API endpoints."""
from typing import Any, Optional, Dict, List
from rest_framework.response import Response
from rest_framework import status as http_status


class SuccessResponse(Response):
    """Standard success response format."""
    
    def __init__(
        self,
        data: Any = None,
        message: str = "Success",
        status_code: int = http_status.HTTP_200_OK,
        headers: Optional[Dict] = None,
        **kwargs
    ):
        response_data = {
            "success": True,
            "message": message,
            "data": data,
        }
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status_code, headers=headers)


class ErrorResponse(Response):
    """Standard error response format."""
    
    def __init__(
        self,
        message: str = "An error occurred",
        errors: Optional[Dict[str, Any]] = None,
        error_code: str = "INTERNAL_ERROR",
        status_code: int = http_status.HTTP_400_BAD_REQUEST,
        headers: Optional[Dict] = None,
        **kwargs
    ):
        response_data = {
            "success": False,
            "message": message,
            "error_code": error_code,
            "errors": errors or {},
        }
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status_code, headers=headers)


class PaginatedResponse(Response):
    """Pagination-aware success response."""
    
    def __init__(
        self,
        data: List[Any],
        page: int = 1,
        page_size: int = 20,
        total_count: int = 0,
        total_pages: int = 0,
        message: str = "Success",
        status_code: int = http_status.HTTP_200_OK,
        headers: Optional[Dict] = None,
        **kwargs
    ):
        response_data = {
            "success": True,
            "message": message,
            "data": data,
            "pagination": {
                "page": page,
                "page_size": page_size,
                "total_count": total_count,
                "total_pages": total_pages,
            },
        }
        response_data.update(kwargs)
        super().__init__(data=response_data, status=status_code, headers=headers)
