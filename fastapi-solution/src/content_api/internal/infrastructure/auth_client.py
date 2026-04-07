import grpc
from Auth_sprint_2.v1 import auth_pb2
from Auth_sprint_2.v1 import auth_pb2_grpc
from Auth_sprint_2.v1 import request_context_pb2
from fastapi import status

from content_api.internal.infrastructure.circuit_breaker import circuit_breaker
from content_api.internal.ports.output.auth_verifier import (
    AuthServiceUnavailableError,
    AuthUserIdentity,
    AuthVerifyResult, AuthVerifier,
)


class AuthGrpcClient(AuthVerifier):
    def __init__(
            self,
            host: str,
            port: int,
            timeout_seconds: float,
    ):
        self._target = f"{host}:{port}"
        self._timeout_seconds = timeout_seconds

    @circuit_breaker(
        state_count=15,
        error_count=5,
        network_errors=[grpc.RpcError],
        sleep_time_sec=0.2,
        open_error=AuthServiceUnavailableError,
    )
    async def verify_token(
            self,
            access_token: str,
            request_id: str,
            user_agent: str,
            ip_address: str,
    ) -> AuthVerifyResult:
        async with grpc.aio.insecure_channel(self._target) as channel:
            stub = auth_pb2_grpc.AuthServiceStub(channel)
            response = await stub.VerifyToken(
                auth_pb2.VerifyTokenRequest(
                    access_token=access_token,
                    context=request_context_pb2.RequestContext(
                        request_id=request_id,
                        user_agent=user_agent,
                        ip_address=ip_address,
                    ),
                ),
                timeout=self._timeout_seconds,
            )

        if response.HasField("user"):
            return AuthVerifyResult(
                status_code=status.HTTP_200_OK,
                user=AuthUserIdentity(
                    user_id=response.user.user_id,
                    roles=tuple(response.user.roles),
                    is_superuser=response.user.is_superuser,
                ),
            )

        return AuthVerifyResult(
            status_code=status.HTTP_401_UNAUTHORIZED,
            error_code=response.error.code
            if response.HasField("error")
            else None,
        )
