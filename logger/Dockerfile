FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt

COPY mqtt_logger.py .

CMD ["python", "-u", "mqtt_logger.py"]
