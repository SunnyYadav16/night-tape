# Freeze image for the Week 6 clean-room dry run. Record this digest in the freeze archive.
FROM python:3.12-slim-bookworm@sha256:392307d22300de8b5986851a12d9176dfc0fc073e65bf6523ebd7dcbeb23564e
COPY --from=ghcr.io/astral-sh/uv:0.7.12 /uv /uvx /bin/
ENV TZ=UTC LANG=C.UTF-8 UV_LINK_MODE=copy UV_PYTHON_DOWNLOADS=never UV_PROJECT_ENVIRONMENT=/opt/venv
RUN apt-get update && apt-get install -y --no-install-recommends make git \
    && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock .python-version ./
RUN uv sync --frozen --no-install-project
RUN uv run --no-sync playwright install --with-deps chromium
COPY . .
RUN uv sync --frozen
CMD ["make", "test"]
