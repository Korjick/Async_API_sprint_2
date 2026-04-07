from dataclasses import dataclass
from typing import Optional, Protocol


class AuthServiceUnavailableError(Exception):
    pass


@dataclass(frozen=True)
class AuthUserIdentity:
    user_id: str
    roles: tuple[str, ...]
    is_superuser: bool


@dataclass(frozen=True)
class AuthVerifyResult:
    status_code: int
    user: Optional[AuthUserIdentity] = None
    error_code: Optional[int] = None


class AuthVerifier(Protocol):
    async def verify_token(
            self,
            access_token: str,
            request_id: str,
            user_agent: str,
            ip_address: str,
    ) -> AuthVerifyResult:
        pass


instance: Optional[AuthVerifier] = None


def get_instance() -> AuthVerifier:
    if instance is None:
        raise RuntimeError("Auth verifier is not initialized")
    return instance
