FROM python:3.10.8-alpine3.15

WORKDIR /snippman
COPY . .

RUN apk add gcc g++
RUN python -m pip install --prefix=/usr/local --no-cache-dir --upgrade pip \
    && ARCHFLAGS=-Wno-error=unused-command-line-argument-hard-error-in-future pip install --upgrade numpy \
    && pip install --prefix=/usr/local --no-cache-dir -r requirements.txt

CMD ["/snippman/run.py"]
ENTRYPOINT ["python"]
