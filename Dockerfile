FROM python:3.11-slim AS Builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 

WORKDIR /build

RUN python -m venv /opt/venv

ENV PATH="/opt/venv/bin:$PATH"

COPY requirements.txt .

RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt





FROM python:3.11-slim AS Runner

ENV PYTHONDONTWRITEBYTECODE=1\
    PYTHONUNBUFFERED=1\
    PATH="/opt/venv/bin:$PATH"

RUN useradd -m -s /bin/bash appuser

WORKDIR /code

COPY --from=Builder /opt/venv /opt/venv

COPY ./app /code/app

RUN chown -R appuser:appuser /code

USER appuser

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]


