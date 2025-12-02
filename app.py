import logging
from flask import Flask, request

from opentelemetry.sdk.resources import Resource

from opentelemetry._logs import set_logger_provider
from opentelemetry.exporter.otlp.proto.grpc._log_exporter import OTLPLogExporter
from opentelemetry.sdk._logs import LoggerProvider, LoggingHandler
from opentelemetry.sdk._logs.export import BatchLogRecordProcessor

from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.semconv.trace import SpanAttributes

from opentelemetry import metrics
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.exporter.otlp.proto.grpc.metric_exporter import OTLPMetricExporter
from opentelemetry.sdk.metrics.export import PeriodicExportingMetricReader

# Initialize Flask app
app = Flask(__name__)

# this assumes an OTLP collector is running locally on default port.  Adjust as needed.
OTLP_COLLECTOR = "localhost:4317"

# Initialize OpenTelemetry components will included with metrics, traces, and logs
RESOURCE = Resource.create(attributes={
  "service.name": "otel-python-demo"
})

# initialize metrics exporter, provider, and meter
metric_otlp_exporter = OTLPMetricExporter(endpoint=OTLP_COLLECTOR, insecure=True)
metric_reader = PeriodicExportingMetricReader(metric_otlp_exporter)
metric_provider=MeterProvider(resource=RESOURCE,metric_readers=[metric_reader])
metrics.set_meter_provider(metric_provider)

# initialize a counter metric
meter = metrics.get_meter(__name__)
request_counter = meter.create_counter(
   name="demo.metric.my_metric",
   description="Demo Metric."
)

# initialize traces exporter and provider
trace_provider = TracerProvider(resource=RESOURCE)
trace.set_tracer_provider(trace_provider)
span_exporter = OTLPSpanExporter(endpoint=OTLP_COLLECTOR, insecure=True, )
span_processor = BatchSpanProcessor(span_exporter)
trace_provider.add_span_processor(span_processor)

# initialize logger exporter and provider
logger_provider = LoggerProvider(resource=RESOURCE)
set_logger_provider(logger_provider)
log_exporter = OTLPLogExporter(endpoint=OTLP_COLLECTOR, insecure=True)
logger_provider.add_log_record_processor(BatchLogRecordProcessor(log_exporter))

# Set the logging level to decide what levels get sent
handler = LoggingHandler(level=logging.NOTSET, logger_provider=logger_provider)

# Attach OTLP handler to root logger
logging.getLogger().addHandler(handler)

# Define Flask routes
@app.route('/')
def index():
    # Metric increment
    request_counter.add(1, {"http.route": request.path})
    return "Welcome to the OpenTelemetry Flask API!\n"

@app.route('/log', methods=['GET'])
def log_message():
    # Metric increment
    request_counter.add(1, {"http.route": request.path})
    # Log message
    query = request.args.get('q', 'test log')
    logging.warning("This is a warning log message. " + query)
    logging.error("This is an error log message. " + query)
    return "Log message sent. " + query + "\n"

@app.route('/trace', methods=['GET'])
def trace_message():
    # Metric increment
    request_counter.add(1, {"http.route": request.path})
    # Trace message
    tracer = trace.get_tracer(__name__)
    query = request.args.get('q', 'test trace')
    with tracer.start_as_current_span("parent " + query):
        # add attribute to parent span
        current_span = trace.get_current_span()
        current_span.set_attribute(SpanAttributes.HTTP_URL, "https://demoapp.com/")
        # Log message to parent span
        logging.error("This is an error log message with trace context. parent " + query)
        # add child span with log message
        with tracer.start_as_current_span("child " + query) as child:
          logging.error("This is an error log message with trace context. child " + query)
    return "Trace message sent. " + query + "\n"

if __name__ == '__main__':
    # Disable Flask's default access logs (Werkzeug logger)
    import logging as log
    log.getLogger('werkzeug').setLevel(log.ERROR)
    
    app.run(host='0.0.0.0', port=5000)