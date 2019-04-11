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


__all__ = (
    'VaultProvider',
    'GPGProvider',
    'OpenSSLProvider'
)


class VaultProvider(Provider):
    """
    This is the original Provider which uses HashiCorp Vault to fetch secrets.
    """
    def __init__(
            self,
            paths: str = None,
            token: str = os.environ.get("VAULTIFY_SECRET"),
            addr: str = None
    ):

        self.token = os.environ.get("VAULT_TOKEN", token)
        self.addr = os.environ.get("VAULT_ADDR", addr)
        self.paths = os.environ.get("VAULT_PATHS", paths).split(',')

        self.client = hvac.Client(
            url=self.addr,
            token=self.token
            )
        logger.debug('VaultProvider initialized')

    def get_secrets(self):
        """
        Fetch all the leaves from vaults KV tree and return a generator with
        the values.
        """
        secrets = {}
        for path in self.paths:
            secrets[path] = self.client.read(path)["data"]
            logger.info(
                'provided secrets from {}'.format(path))
        return secrets


class OpenSSLProvider(Provider):
    """
    Decrypt and provide secrets from a static file encrypted symmetrically with
    OpenSSL.

    """
    def __init__(self, secret: str):  
        self.secret = os.environ.get('VAULTIFY_SECRET', secret)
        self.popen_kwargs = dict(
            bufsize=-1,
            executable='/usr/bin/openssl',
            universal_newlines=True,
            encoding='utf-8',
            stderr=PIPE,
            stdout=PIPE
            )
        logger.debug('OpenSSLProvider initialized')

    def get_secrets(self):
        """
        This implementation uses a preexisting openssl from the host system to
        run a command equivalent to:

        `openssl aes-256-cbc -d -a -in <symmetrically-encrypted.enc>`

        The file should be created with this command:

        `openssl enc -aes-256-cbc -salt -a -in <file> -out <file>.enc`

            where:
                   `-salt` is recommended to prevent dictionary attacks
                   '-a' is used to output an ascii-armored cipher text

        TODO(CWE-546):
            while us.gov uses AES256 for top secret data,
            aes-256-cbc is a bad choice and we should push for a openssl version
            that has aes-256-gcm to protect against a padding oracle in CBC modes.
            TLDR: prefer an openssl version compiled with AEAD to allow aes-256-gcm

        """
        secrets = {}
        for filename in glob.glob('./assets/*.enc'):
            out = run_process(
                ['openssl', 'aes-256-cbc',
                 '-d', '-a',
                 '-in', filename,
                 '-k', self.secret],
                self.popen_kwargs
            )

            secrets[filename] = env2dict(out)
            logger.info(
                'provided secrets from {}'.format(filename))
        return secrets


class GPGProvider(Provider):
    """
    Decrypt and provide secrets from a static gpg file encrypted symmetrically.
    """
    def __init__(self, secret: str):  # nosec
        self.secret = os.environ.get('VAULTIFY_SECRET', secret)
        self.popen_kwargs = dict(
            bufsize=-1,
            executable='/usr/bin/gpg',
            universal_newlines=True,
            encoding='utf-8',
            stderr=PIPE,
            stdout=PIPE
            )
        logger.debug('GPGProvider initialised')

    def get_secrets(self):
        """
        This implementation uses a preexisting gpg binary from the host system
        to run a command equivalent to `gpg -qd <symmetrically-encypted.gpg>`

        """
        secrets = {}
        for filename in glob.glob('./assets/*.gpg'):
            out = run_process(
                ['gpg', '-qd',
                 '--yes', '--batch',
                 '--passphrase={}'.format(self.secret),
                 filename],
                self.popen_kwargs
                )
            secrets[filename] = env2dict(out)
            logger.info(
                'provided secrets from {}'.format(filename))

        return secrets
