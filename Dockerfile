FROM python:3.6.4-alpine3.7 as production

WORKDIR /code
COPY requirements.txt .

RUN mkdir secrets \
 && apk add --no-cache \
    gnupg\
    openssl\
 && pip3 install -r requirements.txt\
 && adduser -D vaultify\
 && chown vaultify .

COPY ./vaultify vaultify
COPY ./entry.py entry.py

USER vaultify

ENTRYPOINT ["python3"]
CMD ["/code/entry.py"]
