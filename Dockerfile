FROM tiangolo/uvicorn-gunicorn-fastapi:python3.9-slim

COPY ./requirements.txt /app/requirements.txt

RUN apt-get update && apt-get install -y git
RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app