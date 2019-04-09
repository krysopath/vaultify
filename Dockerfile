FROM python:3.6.4-alpine3.7 as production

WORKDIR /code
COPY requirements.txt .

RUN mkdir secrets \
 && apk add --no-cache gnupg \
 && pip3 install -r requirements.txt

COPY ./vaultify vaultify
COPY ./entry.py entry.py

ENTRYPOINT ["python3", "/code/entry.py"]
