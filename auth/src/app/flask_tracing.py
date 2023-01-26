from flask import Flask, request
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider, Span
from opentelemetry.sdk.resources import Resource
from opentelemetry.instrumentation.flask import FlaskInstrumentor
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.exporter.jaeger.thrift import JaegerExporter


def configure_tracer(app) -> None:
    provider = TracerProvider(resource=Resource.create({"service.name": app.config["SERVICE_NAME"]}))
    # Sets the global default tracer provider
    trace.set_tracer_provider(provider)

    jaeger_exporter = JaegerExporter(agent_host_name=app.config["JAEGER_HOST_NAME"],agent_port=app.config["JAEGER_PORT"])
    provider.add_span_processor(BatchSpanProcessor(jaeger_exporter))

    if app.config["DEBUG"]:
        console_exporter = ConsoleSpanExporter()
        provider.add_span_processor(BatchSpanProcessor(console_exporter))


def request_hook(span: Span, environ: "WSGIEnvironment"):
    request_id = request.headers.get('X-Request-Id')
    if span and span.is_recording():
        span.set_attribute('http.request_id', request_id)


def init_tracer(app: Flask) -> None:
    configure_tracer(app)
    FlaskInstrumentor().instrument_app(app, request_hook=request_hook)
