# syntax=docker/dockerfile:1.21
ARG UV_IMAGE=ghcr.io/astral-sh/uv:0.10
FROM ${UV_IMAGE} AS uv

FROM public.ecr.aws/docker/library/python:3.14-slim
ARG DEBIAN_FRONTEND=noninteractive

RUN --mount=type=cache,target=/var/cache/apt,sharing=locked \
    --mount=type=cache,target=/var/lib/apt/lists,sharing=locked \
    apt-get -qq update && apt-get -qq install --no-install-recommends -y git > /dev/null \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

COPY --from=uv /uv /bin/
WORKDIR /app
COPY pyproject.toml uv.lock /app/
ENV UV_PROJECT_ENVIRONMENT=/opt/venv
RUN --mount=type=cache,target=/root/.cache/uv,sharing=locked \
    uv sync --frozen --no-install-project --no-dev
ENV VIRTUAL_ENV=/opt/venv
ENV PATH="/opt/venv/bin:$PATH"

RUN useradd -m appuser
COPY --chown=appuser:appuser . /app
RUN chown -R appuser:appuser /opt/venv
USER appuser

WORKDIR /app
RUN git config --global pull.rebase true
CMD ["uv", "run", "python", "-m", "droos_bot"]
