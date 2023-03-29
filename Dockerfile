FROM python:3.11-slim

RUN apt-get upgrade -y && \
    apt-get update && \
    apt-get install -y --no-install-recommends \
        build-essential default-libmysqlclient-dev git netcat && \
    apt-get clean -y

WORKDIR /app

COPY requirements.txt .
RUN pip install -r /app/requirements.txt

CMD ["./start.sh"]
