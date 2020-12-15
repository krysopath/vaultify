#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements various secret Provider classes.
"""

import logging
import os
import glob
from subprocess import PIPE
import hvac
from .util import env2dict, run_process
from .base import Provider

logger = logging.getLogger(__name__)


__all__ = ("VaultProvider", "GPGProvider", "OpenSSLProvider", "PlainTextProvider")


class VaultProvider(Provider):
    """
    This is the original Provider which uses HashiCorp Vault to fetch secrets.
    """

    def __init__(
        self,
        paths: str = None,
        token: str = os.environ.get("VAULTIFY_SECRET"),
        addr: str = None,
    ):

        self.token = os.environ.get("VAULT_TOKEN", token)
        self.addr = os.environ.get("VAULT_ADDR", addr)
        self.paths = os.environ.get("VAULT_PATHS", paths).split(",")

        self.client = hvac.Client(url=self.addr, token=self.token)
        logger.debug("VaultProvider initialized")

    def get_secrets(self):
        """
        Fetch all the leaves from vaults KV tree and return a generator with
        the values.
        """
        secrets = {}
        for path in self.paths:
            secrets[path] = self.client.read(path)["data"]
            logger.info("provided secrets from {}".format(path))
        return secrets


class OpenSSLProvider(Provider):
    """
    Decrypt and provide secrets from a static file encrypted symmetrically with
    OpenSSL.

    >>> OpenSSLProvider(secret='abc').get_secrets()
    {'./assets/test.enc': {'K1': 'V1', 'K2': 'V2'}}
    """

    def __init__(self, secret: str, cipher: str = "aes-256-cbc", md: str = "sha256"):
        self.secret = secret
        self.cipher = cipher
        self.md = md
        self.popen_kwargs = dict(
            bufsize=-1,
            executable="/usr/bin/openssl",
            universal_newlines=True,
            encoding="utf-8",
            stderr=PIPE,
            stdout=PIPE,
        )
        logger.debug("OpenSSLProvider initialized")

    def get_secrets(self):
        """
        This implementation uses a preexisting openssl from the host system to
        run a command equivalent to:
        `openssl aes-256-cbc -md sha256 -d -a -in <symmetrically-encrypted.enc>`

        """
        secrets = {}
        for filename in glob.glob("./assets/*.enc"):
            out = run_process(
                [
                    "openssl",
                    self.cipher,
                    "-d",
                    "-a",
                    "-md",
                    self.md,
                    "-in",
                    filename,
                    "-k",
                    self.secret,
                ],
                self.popen_kwargs,
            )

            secrets[filename] = env2dict(out)
            logger.info("provided secrets from {}".format(filename))
            return secrets


class GPGProvider(Provider):
    """
    Decrypt and provide secrets from a static gpg file encrypted symmetrically.
    >>> GPGProvider(secret='abc').get_secrets()
    {'./assets/test.gpg': {'K1': 'V1', 'K2': 'V2'}}
    """

    def __init__(self, secret: str):  # nosec
        self.secret = secret
        self.popen_kwargs = dict(
            bufsize=-1,
            executable="/usr/bin/gpg",
            universal_newlines=True,
            encoding="utf-8",
            stderr=PIPE,
            stdout=PIPE,
        )
        logger.debug("GPGProvider initialised")

    def get_secrets(self):
        """
        This implementation uses a preexisting gpg binary from the host system
        to run a command equivalent to `gpg -qd <symmetrically-encypted.gpg>`
        """
        secrets = {}
        for filename in glob.glob("./assets/*.gpg"):
            out = run_process(
                [
                    "gpg",
                    "-qd",
                    "--yes",
                    "--batch",
                    "--passphrase={}".format(self.secret),
                    filename,
                ],
                self.popen_kwargs,
            )
            secrets[filename] = env2dict(out)
            logger.info("provided secrets from {}".format(filename))

        return secrets


class PlainTextProvider(Provider):
    """
    >>> PlainTextProvider().get_secrets()
    {'./assets/secrets.plain': {'K1': 'V1', 'K2': 'V2'}}
    """

    def __init__(self):
        logger.debug("GPGProvider initialised")

    def get_secrets(self):
        secrets = {}
        for filename in glob.glob("./assets/*.plain"):
            with open(filename, "r") as infile:
                out = infile.read()
                secrets[filename] = env2dict(out)
            logger.info("provided secrets from {}".format(filename))

        return secrets
