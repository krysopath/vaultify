ARG BASE_IMAGE

FROM python:$BASE_IMAGE as developement
WORKDIR /code
COPY requirements.txt .
RUN mkdir secrets assets\
 && apk add --no-cache \
    gnupg\
    openssl\
    make\
 && pip3 install -r requirements.txt\
 && adduser -D vaultify\
 && chown vaultify .
COPY ./Makefile Makefile
COPY ./vaultify vaultify
COPY .vaultify.yml ./vaultify.yml
COPY ./entry.py entry.py
COPY ./setup.py setup.py
COPY ./tests tests
COPY ./runtests.py runtests.py
RUN make run/tests
RUN make artifact/pkg
USER vaultify
ENTRYPOINT ["python3"]
CMD ["/code/entry.py", "{*}"]

FROM python:$BASE_IMAGE as production
WORKDIR /code
COPY --from=0 /code/dist/vaultify*.whl /code/
COPY --from=0 /code/requirements.txt .
RUN mkdir secrets assets\
 && apk add --no-cache \
    gnupg\
    openssl\
 && pip3 install -r requirements.txt\
 && pip3 install vaultify*.whl\
 && adduser -D vaultify\
 && chown vaultify .
USER vaultify
ENTRYPOINT ["vaultify"]
