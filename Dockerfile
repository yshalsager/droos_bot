FROM python:3.14-slim
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get -qq install --no-install-recommends -y git > /dev/null \
&& apt-get clean  && rm -rf /var/lib/apt/lists/*

COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/
WORKDIR /code
COPY pyproject.toml uv.lock /code/
RUN uv sync --frozen --no-cache
ENV PATH="/code/.venv/bin:$PATH"

RUN useradd -m appuser
USER appuser

WORKDIR /code/app
RUN git config --global pull.rebase true
#COPY --chown=appuser:appuser . .
#CMD ["python3", "-m", "droos_bot"]
