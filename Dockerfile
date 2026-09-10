FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

RUN chmod +x /app/entrypoint.sh /app/gunicorn_run.py && sed -i 's/\r$//' /app/entrypoint.sh /app/gunicorn_run.py
RUN cp /app/gunicorn_run.py /usr/local/bin/gunicorn && chmod +x /usr/local/bin/gunicorn

EXPOSE 8000

CMD ["/app/entrypoint.sh"]

