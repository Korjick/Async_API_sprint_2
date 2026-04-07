from fastapi import FastAPI
from opentelemetry import trace
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import \
    OTLPSpanExporter
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.grpc import GrpcAioInstrumentorClient
from opentelemetry.sdk.resources import Resource, SERVICE_NAME, SERVICE_VERSION
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

from content_api.internal.infrastructure.app_config import Settings

_tracer_provider: TracerProvider | None = None


def setup_telemetry(app: FastAPI, settings: Settings) -> None:
    if not settings.otel_enabled:
        return

    _configure_tracer_provider(settings)
    FastAPIInstrumentor.instrument_app(app)
    GrpcAioInstrumentorClient().instrument()


def shutdown_telemetry() -> None:
    if _tracer_provider is None:
        return
    _tracer_provider.shutdown()


def _configure_tracer_provider(settings: Settings) -> None:
    global _tracer_provider
    if _tracer_provider is not None:
        return

    resource = Resource.create(
        {
            SERVICE_NAME: settings.otel_service_name,
            SERVICE_VERSION: settings.otel_service_version,
            "deployment.environment": settings.otel_environment,
        }
    )
    provider = TracerProvider(resource=resource)
    span_exporter = OTLPSpanExporter(
        endpoint=settings.otel_exporter_otlp_endpoint,
        insecure=settings.otel_exporter_otlp_insecure,
    )
    provider.add_span_processor(BatchSpanProcessor(span_exporter))
    trace.set_tracer_provider(provider)
    _tracer_provider = provider
