FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt /app/
COPY wheels /app/wheels/

RUN pip install --no-index --find-links=./wheels -r requirements.txt

COPY . /app

ENV PYTHONUNBUFFERED=1

CMD ["sh", "-c", "python /app/${SCRIPT}"]