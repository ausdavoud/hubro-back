from rest_framework import status
from rest_framework.exceptions import APIException

from common.views.error_codes import ErrorCodes


class InvalidCategoryError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, supplier_id: int, category: str):
        detail = {
            "error": {
                "code": ErrorCodes.INVALID_CATEGORY,
                "description": f"The category <{category}> is not valid for supplier <{supplier_id}>.",
            }
        }
        super().__init__(detail)


class ForbiddenSupplierAssignmentError(APIException):
    status_code = status.HTTP_400_BAD_REQUEST

    def __init__(self, category: str):
        detail = {
            "error": {
                "code": ErrorCodes.FORBIDDEN_SUPPLIER_ASSIGNMENT,
                "description": f"The research for <{category}> R&D item has not been completed yet",
            }
        }
        super().__init__(detail)
