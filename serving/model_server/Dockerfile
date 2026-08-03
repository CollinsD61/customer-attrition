FROM python:3.11-slim

WORKDIR /app

# Install libgomp1 for LightGBM
RUN apt-get update && apt-get install -y --no-install-recommends libgomp1 && rm -rf /var/lib/apt/lists/*

COPY serving/model_server/requirements.txt requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

COPY serving/model_server /app/serving/model_server
COPY mlops /app/mlops

# Set PYTHONPATH so the serving and mlops modules can be resolved
ENV PYTHONPATH=/app

ENTRYPOINT ["python", "-m", "serving.model_server.app"]
