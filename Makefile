TARGET := production
BASE_IMAGE := 3.7-alpine3.7

ci: run/tests\
	artifact/pkg\
	artifact/docker\
	artifact/tag

dev/ci:
	ls vaultify/*py Dockerfile .vaultify.yml | entr -s 'make ci'

artifact/pkg:
	python3 setup.py sdist bdist_wheel

artifact/docker: Dockerfile
	docker build \
	    --build-arg BASE_IMAGE=$(BASE_IMAGE)\
	    -t vaultify:$(shell git rev-parse --short HEAD)\
	    --target $(TARGET)\
	    . 
	docker tag\
	    vaultify:$(shell git rev-parse --short HEAD)\
	    vaultify:$(shell git describe --abbrev=0 --tags)-py$(BASE_IMAGE)

artifact/tag:
	docker tag\
		vaultify:$(shell git rev-parse --short HEAD)\
		vaultify:$(shell git describe --abbrev=0 --tags)

run/tests:
	rm -rf tests/new* assets/*
	gpg \
	    --symmetric\
	    --batch\
	    --passphrase=abc\
	    -o assets/test.gpg\
	    tests/secrets.env

	openssl enc \
	    -k abc \
	    -aes-256-cbc \
	    -salt \
	    -a \
	    -in tests/secrets.env \
	    -out assets/test.enc

	VAULTIFY_LOG_LEVEL=WARNING python3 runtests.py

manual:
	@groff -man -Tascii man/vaultify.1

dev/install/packaging:
	python3 -m pip install --user --upgrade pip setuptools wheel

dev/install/os:
	sudo apt-get install gnupg openssl
