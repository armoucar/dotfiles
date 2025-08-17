import os
import httpx
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.sdk.resources import Resource
from openinference.semconv.resource import ResourceAttributes


def initialize_telemetry():
    """Initialize OpenTelemetry and OpenInference instrumentation for OpenAI."""
    endpoint = os.environ.get("OPENTELEMETRY_ENDPOINT", "http://127.0.0.1:6006/v1/traces")
    
    # Check if server is available
    base_url = endpoint.rsplit("/v1/traces", 1)[0]
    try:
        httpx.get(f"{base_url}/v1/projects", timeout=2)
    except:
        return None

    # Setup telemetry
    resource = Resource(attributes={ResourceAttributes.PROJECT_NAME: "dot"})
    tracer_provider = trace_sdk.TracerProvider(resource=resource)
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

    if os.environ.get("OPENTELEMETRY_DEBUG", "").lower() in ("true", "1", "yes"):
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)
    return tracer_provider
