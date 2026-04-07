from typing import Optional

from fastapi import Header, HTTPException, Request, status

from content_api.internal.ports.output.auth_verifier import (
    AuthServiceUnavailableError,
    AuthUserIdentity,
    get_instance as get_auth_client,
)
from content_api.internal.ports.output.logger import Logger

AUTH_SCHEME = "Bearer"


def _extract_schema(authorization: Optional[str]) -> Optional[str]:
    if authorization is None:
        return None

    parts = authorization.split()
    if len(parts) != 2 or parts[0].lower() != AUTH_SCHEME.lower():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header",
        )
    token = parts[1].strip()
    if not token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is required",
        )
    return token


async def optional_auth_identity(
        request: Request,
        authorization: Optional[str] = Header(default=None),
) -> Optional[AuthUserIdentity]:
    logger: Logger = request.app.state.logger.branch(component="auth_dependency")
    access_token = _extract_schema(authorization)
    if access_token is None:
        return None

    client = get_auth_client()
    try:
        result = await client.verify_token(
            access_token=access_token,
            request_id=request.headers.get("x-request-id", ""),
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
        )
    except AuthServiceUnavailableError:
        logger.warning("auth_service_unavailable", mode="optional")
        return None

    if result.status_code != status.HTTP_200_OK or result.user is None:
        logger.info(
            "auth_token_invalid",
            mode="optional",
            status_code=result.status_code,
            error_code=result.error_code,
        )
        return None

    request.state.auth_user = result.user
    return result.user


async def required_auth_identity(
        request: Request,
        authorization: Optional[str] = Header(default=None),
) -> AuthUserIdentity:
    logger: Logger = request.app.state.logger.branch(component="auth_dependency")
    access_token = _extract_schema(authorization)
    if access_token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authorization required",
        )

    client = get_auth_client()
    try:
        result = await client.verify_token(
            access_token=access_token,
            request_id=request.headers.get("x-request-id", ""),
            user_agent=request.headers.get("user-agent", ""),
            ip_address=request.client.host if request.client else "",
        )
    except AuthServiceUnavailableError:
        logger.warning("auth_service_unavailable", mode="required")
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Auth service unavailable",
        )

    if result.status_code != status.HTTP_200_OK or result.user is None:
        logger.info(
            "auth_token_invalid",
            mode="required",
            status_code=result.status_code,
            error_code=result.error_code,
        )
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token is invalid",
        )

    request.state.auth_user = result.user
    return result.user
