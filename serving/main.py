import numpy as np
import os
from time import time
from loguru import logger
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
from services.mlp_service import MultiLayerPerceptronService
from src.models.mlp.config import MLPConfig
from opentelemetry import metrics, trace
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from opentelemetry.metrics import set_meter_provider
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.trace import get_tracer_provider, set_tracer_provider
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from prometheus_client import start_http_server

model = {}

# Start Prometheus client
start_http_server(port=os.getenv("PROMETHEUS_PORT"), addr=os.getenv("DOCKER_NETWORK_IP"))

# Service name is required for most backends
resource = Resource(attributes={SERVICE_NAME: "emotiai-service"})

# Exporter to export metrics to Prometheus
reader = PrometheusMetricReader()

# Meter is responsible for creating and recording metrics
provider = MeterProvider(resource=resource, metric_readers=[reader])
set_meter_provider(provider)
meter = metrics.get_meter("emotiai-service")

# Tracer 
set_tracer_provider(
    TracerProvider(resource=Resource.create({SERVICE_NAME: "emotiai-service"}))
)
tracer = get_tracer_provider().get_tracer("emotiai-service")
jaeger_exporter = JaegerExporter(
    agent_host_name=os.getenv("DOCKER_NETWORK_IP"),
    agent_port=os.getenv("JAEGER_PORT"),
)
span_processor = BatchSpanProcessor(jaeger_exporter)
get_tracer_provider().add_span_processor(span_processor)

# Create your first counter
counter = meter.create_counter(
    name="emotion_classification_request_counter",
    description="Number of emotion classification requests"
)

histogram = meter.create_histogram(
    name="emotion_classification_response_histogram",
    description="Emotion classification response histogram",
    unit="seconds",
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    model["mlp"] = MultiLayerPerceptronService('mlp', MLPConfig.SEQUENCE_LENGTH, MLPConfig.OUTPUT_MODE)
    yield
    model.clear()

app = FastAPI(lifespan=lifespan)

@app.post("/mlp", response_model=dict)
async def MLP(prompt: str):
    try:
        # Mark the starting point for the response
        starting_time = time()
        with tracer.start_as_current_span("processors") as processors:
            with tracer.start_as_current_span(
                "make-prediction", links=[trace.Link(processors.get_span_context())]
            ):
                pred = model["mlp"].predict(prompt)["predictions"]

            with tracer.start_as_current_span(
                "filter-result", links=[trace.Link(processors.get_span_context())]
            ):
                result = np.argwhere(pred > 0.5)
            
            with tracer.start_as_current_span(
                "postprocess-result", links=[trace.Link(processors.get_span_context())]
            ):
                classnames = [
                    "admiration",
                    "amusement",
                    "anger",
                    "annoyance",
                    "approval",
                    "caring",
                    "confusion",
                    "curiosity",
                    "desire",
                    "disappointment",
                    "disapproval",
                    "disgust",
                    "embarrassment",
                    "excitement",
                    "fear",
                    "gratitude",
                    "grief",
                    "joy",
                    "love",
                    "nervousness",
                    "optimism",
                    "pride",
                    "realization",
                    "relief",
                    "remorse",
                    "sadness",
                    "surprise",
                    "neutral"
                ]

                postprocessed_result = [classnames[i] for i in result[0]]

        # Labels for all metrics
        label = {"api": "/mlp"}

        counter.add(10, label)

        # Mark the end of the response
        ending_time = time()
        elapsed_time = ending_time - starting_time

        # Add histogram
        logger.info("elapsed time: ", elapsed_time)
        logger.info(elapsed_time)
        histogram.record(elapsed_time, label)

        return {"prediction": postprocessed_result}
    except Exception as error:
        raise HTTPException(status_code=500, detail="Failed to classify input prompt.")