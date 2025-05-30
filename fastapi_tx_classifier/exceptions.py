from fastapi import HTTPException


class AppError(HTTPException):
    def __init__(self, status_code: int, code: str, message: str):
        detail = {"code": code, "message": message}
        super().__init__(status_code=status_code, detail=detail)
