# ---- base ----
FROM python:3.11-slim AS base
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1
WORKDIR /app

# 系统依赖（curl/git、libpq、playwright 依赖）
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl git build-essential libpq-dev ffmpeg \
    libglib2.0-0 libnss3 libatk1.0-0 libatk-bridge2.0-0 libcups2 libdrm2 \
    libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 \
    libasound2 libxshmfence1 libx11-xcb1 libx11-6 libxcb1 libxext6 libxss1 \
    && rm -rf /var/lib/apt/lists/*

# ---- install deps ----
COPY pyproject.toml poetry.lock* /app/
RUN pip install --no-cache-dir poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi --no-root

# playwright（TikTok 用）仅装 chromium
# RUN python -m playwright install --with-deps chromium

# ---- app ----
COPY app /app/app
COPY migrations /app/migrations

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
