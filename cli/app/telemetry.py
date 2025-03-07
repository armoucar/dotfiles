import os
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk import trace as trace_sdk
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor
from openinference.instrumentation.openai import OpenAIInstrumentor
from opentelemetry.sdk.resources import Resource
from openinference.semconv.resource import ResourceAttributes


def initialize_telemetry():
    """Initialize OpenTelemetry and OpenInference instrumentation for OpenAI."""
    # Default to localhost if not specified
    endpoint = os.environ.get("OPENTELEMETRY_ENDPOINT", "http://127.0.0.1:6006/v1/traces")

    # Setup the tracer provider
    resource = Resource(attributes={ResourceAttributes.PROJECT_NAME: "dot"})
    tracer_provider = trace_sdk.TracerProvider(resource=resource)

    # Add OTLP exporter
    tracer_provider.add_span_processor(SimpleSpanProcessor(OTLPSpanExporter(endpoint)))

    # Optionally add console exporter for debugging
    if os.environ.get("OPENTELEMETRY_DEBUG", "").lower() in ("true", "1", "yes"):
        tracer_provider.add_span_processor(SimpleSpanProcessor(ConsoleSpanExporter()))

    # Instrument OpenAI client
    OpenAIInstrumentor().instrument(tracer_provider=tracer_provider)

    return tracer_provider
