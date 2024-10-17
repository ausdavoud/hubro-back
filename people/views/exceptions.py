from rest_framework import status
from rest_framework.exceptions import APIException

from common.views.error_codes import ErrorCodes


class EmailExists(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, email: str):
        detail = {
            "error": {
                "code": ErrorCodes.EMAIL_EXISTS_CODE,
                "description": "A user with this email already exists",
                "context": {"email": email},
            }
        }
        super().__init__(detail)


class ShortPassword(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        detail = {
            "error": {
                "code": ErrorCodes.SHORT_PASSWORD_CODE,
                "description": "Password should be more than 8 characters",
            }
        }
        super().__init__(detail)


class UserNotCreated(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self):
        detail = {"error": {"code": ErrorCodes.USER_NOT_CREATED_CODE, "description": "User creation failed"}}
        super().__init__(detail)
