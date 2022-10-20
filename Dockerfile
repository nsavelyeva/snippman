# syntax=docker/dockerfile:1

FROM amd64/ubuntu:22.04

ENV URL=http://localhost:8080/
ENV INTERVAL=2
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && apt-get install -y python3-pip python3-dev \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 --no-cache-dir install --upgrade pip \
  && rm -rf /var/lib/apt/lists/*

WORKDIR /snippman
COPY . .
RUN pip3 install -r requirements.txt

CMD ["/snippman/run.py"]
ENTRYPOINT ["python3"]
