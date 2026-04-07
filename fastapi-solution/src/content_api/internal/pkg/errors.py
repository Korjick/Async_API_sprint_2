from typing import Any, Optional


class BaseAppError(Exception):
    """Базовый класс для всех ошибок приложения."""
    pass


class ObjectNotFoundError(BaseAppError):
    _base_msg = "object not found"

    def __init__(self, param_name: str, entity_id: Any,
                 cause: Optional[Exception] = None):
        self.param_name = param_name
        self.entity_id = entity_id
        self.cause = cause

        if cause:
            msg = f"{self._base_msg}: param is: {param_name}, ID is: {entity_id} (cause: {cause})"
        else:
            msg = f"{self._base_msg}: {entity_id}"

        super().__init__(msg)


class ValueIsInvalidError(BaseAppError):
    _base_msg = "value is invalid"

    def __init__(self, param_name: str, cause: Optional[Exception] = None):
        self.param_name = param_name
        self.cause = cause

        if cause:
            msg = f"{self._base_msg}: {param_name} (cause: {cause})"
        else:
            msg = f"{self._base_msg}: {param_name}"

        super().__init__(msg)


class ValueIsRequiredError(BaseAppError):
    _base_msg = "value is required"

    def __init__(self, param_name: str, cause: Optional[Exception] = None):
        self.param_name = param_name
        self.cause = cause

        if cause:
            msg = f"{self._base_msg}: {param_name} (cause: {cause})"
        else:
            msg = f"{self._base_msg}: {param_name}"

        super().__init__(msg)
