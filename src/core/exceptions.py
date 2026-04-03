from datetime import datetime
from src.models.error import ErrorResponse
from fastapi.responses import JSONResponse
from src.main import app

class AppException(Exception):
    def __init__(self, status_code: int, error_code: str, message: str):
        self.status_code = status_code
        self.error_code = error_code
        self.message = message

class NotFoundException(AppException):
    def __init__(self, message="Resource not found"):
        super().__init__( 
            status_code=404,
              error_code="NOT_FOUND",
               
                message=message )
        

class ForbiddenException(AppException):
    def __init__(self, message="Access denied"): 
        super().__init__(
             status_code=403,
               error_code="FORBIDDEN",
                 message=message )
        

class BadRequestException(AppException):
    def __init__(self, message="Bad request"): 
        super().__init__( status_code=400,
                          error_code="BAD_REQUEST",
                            message=message )


@app.exception_handler(AppException)
async def app_exception_handler(request, exc: AppException):
    error = ErrorResponse(
        status_code=exc.status_code,
        error_code=exc.error_code,
        message=exc.message,
       
    )
    return JSONResponse(
        status_code=exc.status_code,
        content=error.dict()
    )
    
