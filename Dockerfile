FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY app ./app
COPY frontend ./frontend
COPY sample_data ./sample_data
RUN pip install --no-cache-dir -e ".[dev]"

EXPOSE 8000 8501
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

