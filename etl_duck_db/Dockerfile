FROM python:3.12-slim

WORKDIR /app

RUN pip install --no-cache-dir uv

COPY pyproject.toml uv.lock README.md ./
COPY src/ ./src/

RUN uv sync --frozen

COPY config/ ./config/
COPY main.py ./

CMD ["uv", "run", "python", "main.py"]