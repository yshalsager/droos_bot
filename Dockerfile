FROM python:3.10-slim AS builder
ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get -qq update && apt-get -qq install --no-install-recommends -y git > /dev/null \
&& apt-get clean  && rm -rf /var/lib/apt/lists/*
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR app
#COPY droos_bot droos_bot
COPY requirements.txt .
RUN pip install -r requirements.txt --user --no-cache --no-warn-script-location

FROM python:3.10-slim
RUN apt-get -qq update && apt-get -qq install --no-install-recommends -y git > /dev/null \
&& apt-get clean  && rm -rf /var/lib/apt/lists/*
RUN git config --global pull.rebase true
ENV PYTHONUNBUFFERED 1
WORKDIR app
ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local
COPY . .
#CMD ['python3', '-m', 'droos_bot']
