from ...models.rd import RDStates


class RDErrorCodes:
    @staticmethod
    def RD_NOT_FOUND(category: str, order: int):
        return {"code": "0103", "description": "R&D item not found", "context": {"category": category, "order": order}}

    @staticmethod
    def RD_STATE_ERROR(state: RDStates):
        return {"code": "0104", "description": "R&D item state is not available", "context": {"state": state}}
