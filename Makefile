TARGET ?= prod
BASE_IMAGE := 3.8-alpine3.10
HEAD ?= $(shell git rev-parse --short HEAD)
TAG ?= $(shell git describe --abbrev=0 --tags)

ci: artifact/pkg\
	artifact/docker\
	artifact/tag

dev/ci:
	ls vaultify/*py Dockerfile .vaultify.yml | entr -s 'make run/tests'

artifact/pkg: clean
	python3 setup.py sdist bdist_wheel

pypi: artifact/pkg
	twine upload --repository-url https://test.pypi.org/legacy/ dist/*

artifact/docker:
	docker build \
	    --build-arg BASE_IMAGE=$(BASE_IMAGE)\
	    -t vaultify:$(HEAD)\
	    --target $(TARGET)\
	    .
	docker tag\
	    vaultify:$(HEAD)\
	    vaultify:$(TAG)-py$(BASE_IMAGE)

artifact/tag:
	docker tag\
		vaultify:$(HEAD)\
		vaultify:$(TAG)

clean:
	rm -rf tests/new* assets/* build/ dist *vaultify.egg*

run/tests: clean
	cp tests/test-config.env assets/secrets.plain
	gpg \
	    --symmetric\
	    --batch\
	    --passphrase=abc\
	    -o assets/test.gpg\
	    tests/secrets.env
	openssl enc\
	    -k abc\
	    -md sha256\
	    -aes-256-cbc\
	    -salt\
	    -a\
	    -in tests/secrets.env\
	    -out assets/test.enc
	VAULTIFY_LOG_LEVEL=DEBUG python3 runtests.py

manual:
	@groff -man -Tascii man/vaultify.1

dev/install/tools:
	python3\
		-m pip\
		install\
		--user\
		--upgrade\
		pip setuptools wheel twine black

dev/install/os:
	sudo apt-get install gnupg openssl

.ONESHELL:
dev/git-init:
		@read -p "enter email: " EMAIL
		read -p "enter public signature-key: " GPG
		git config user.signingKey $${GPG}
		git config user.email $${EMAIL}
		git config commit.gpgSign true
		git config tag.gpgSign true
		git config core.hooksPath .githooks
