FROM python:3.13-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY rembot ./rembot
RUN pip install --no-cache-dir .

CMD ["rembot"]
