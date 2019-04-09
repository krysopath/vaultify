
run/test:
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
