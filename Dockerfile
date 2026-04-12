# Multi-stage build for the Mastermind OpenEnv environment.
#
# This Dockerfile lives at the repo root so both the hackathon validator
# (`docker build $repo`) and the Hugging Face Docker Space build with the
# correct context.

ARG BASE_IMAGE=ghcr.io/meta-pytorch/openenv-base:latest
FROM ${BASE_IMAGE} AS builder

WORKDIR /app

ARG BUILD_MODE=standalone

# Copy environment code (always at root of build context).
COPY . /app/env
WORKDIR /app/env

# Ensure uv is available (for local builds where base image lacks it).
RUN if ! command -v uv >/dev/null 2>&1; then \
        curl -LsSf https://astral.sh/uv/install.sh | sh && \
        mv /root/.local/bin/uv /usr/local/bin/uv && \
        mv /root/.local/bin/uvx /usr/local/bin/uvx; \
    fi

# Install git for building from git repos (build-time only).
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    && rm -rf /var/lib/apt/lists/*

# Install dependencies using uv sync.
# First pass: install dependencies without the project (for better caching).
# Second pass: install the project itself.
RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-install-project --no-editable; \
    else \
        uv sync --no-install-project --no-editable; \
    fi

RUN --mount=type=cache,target=/root/.cache/uv \
    if [ -f uv.lock ]; then \
        uv sync --frozen --no-editable; \
    else \
        uv sync --no-editable; \
    fi

# Final runtime stage.
FROM ${BASE_IMAGE}

WORKDIR /app

# Copy the virtual environment and environment code from builder.
COPY --from=builder /app/env/.venv /app/.venv
COPY --from=builder /app/env /app/env

# Use the virtual environment and expose the repo on PYTHONPATH so
# `server.app:app` resolves from a source-checkout layout.
ENV PATH="/app/.venv/bin:$PATH"
ENV PYTHONPATH="/app/env:$PYTHONPATH"
ENV ENABLE_WEB_INTERFACE="true"

# Health check (portable: no curl/wget needed).
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the FastAPI server.
CMD ["sh", "-c", "cd /app/env && uvicorn server.app:app --host 0.0.0.0 --port 8000"]
