from ddtrace import tracer
from fastapi import FastAPI


def init_telemetry(app: FastAPI) -> None:
    tracer.configure(
        hostname="localhost",
        port=8126,
    )


def get_tracer() -> tracer:
    return tracer
