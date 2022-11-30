FROM python:3.10-slim

WORKDIR /app
COPY requirements.txt .

RUN apt-get upgrade -y && \
    pip install -r /app/requirements.txt
 \
# With `docker compose`, dev. directory already mounted at /app
#COPY . .

CMD ["/bin/cat", "/dev/zero"]
