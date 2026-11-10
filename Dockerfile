FROM ghcr.io/astral-sh/uv:0.13.6 AS uv
FROM python:3.11-slim
COPY --from=uv /uv /usr/local/bin/uv
WORKDIR /app
ENV PYTHONUNBUFFERED=1 MODEL_DIR=/opt/model TIKTOKEN_CACHE_DIR=/opt/tiktoken HF_HUB_DISABLE_XET=1
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --locked --no-dev --no-install-project
COPY src ./src
RUN .venv/bin/python -m src.model_files && .venv/bin/python -c 'import tiktoken; tiktoken.get_encoding("cl100k_base")'
COPY corpus ./corpus
COPY data ./data
RUN useradd --uid 10001 --create-home appuser
USER appuser
EXPOSE 8000
CMD ["sh", "-c", "exec .venv/bin/uvicorn src.app:app --host 0.0.0.0 --port ${PORT:-8000}"]
