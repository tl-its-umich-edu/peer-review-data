FROM python:3.10-slim

WORKDIR /usr/local/src
COPY requirements.txt .

RUN apt-get upgrade -y && \
    pip install -r requirements.txt

COPY . .

CMD ["/bin/cat", "/dev/zero"]
