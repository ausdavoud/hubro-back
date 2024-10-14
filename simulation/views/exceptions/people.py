from rest_framework import status
from rest_framework.exceptions import APIException


class EmailExistsException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, email: str):
        detail = {
            "error": {
                "code": "0001",
                "description": "A user with this email already exists",
                "context": {"email": email},
            }
        }
        super().__init__(detail)


class ShortPasswordException(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self):
        detail = {"error": {"code": "0001", "description": "Password should be more than 8 characters"}}
        super().__init__(detail)


class UserNotCreated(APIException):
    status_code = status.HTTP_500_INTERNAL_SERVER_ERROR

    def __init__(self):
        detail = {"error": {"code": "0001", "description": "User creation failed"}}
        super().__init__(detail)
