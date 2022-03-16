FROM python:3.10-slim AS builder
RUN apt-get -qq update \
&& apt-get -qq install git -y > /dev/null \
&& apt-get clean
ENV PYTHONDONTWRITEBYTECODE 1
WORKDIR app
#COPY droos_bot droos_bot
COPY requirements.txt .
RUN pip install -r requirements.txt --user --no-cache --no-warn-script-location

FROM python:3.10-slim
ENV PYTHONUNBUFFERED 1
WORKDIR app
ENV PATH=/root/.local/bin:$PATH
COPY --from=builder /root/.local /root/.local
COPY . .
#CMD ['python3', '-m', 'droos_bot']
