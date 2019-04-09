#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements Vaultify Consumer classes
"""

import logging
import typing as t
import os
import json
from subprocess import run, PIPE  # nosec
from . import util

from .base import Consumer

__all__ = (
    'DotEnvWriter',
    'JsonWriter',
    'EnvRunner'
)

logger = logging.getLogger(__name__)


class DotEnvWriter(Consumer):
    """
    This Consumer will write secrets as a set of sourceable `export KEY=value`
    lines

    We should fail for existing destination files, when trying to consume:
    >>> DotEnvWriter('/etc/passwd').consume_secrets({"":""})
    Traceback (most recent call last):
       ...
    RuntimeError: /etc/passwd already exists

    We want the dictionary outputted in the right format:
    >>> DotEnvWriter('tests/new.env').consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.env').read()
    "export K1='V1'\\nexport K2='V2'\\n"

    We may specify to overwrite the destination file
    >>> DotEnvWriter(
    ...     'tests/new.env', 
    ...     overwrite=True
    ... ).consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.env').read()
    "export K1='V1'\\nexport K2='V2'\\n"
    

    """
    def __init__(self, path: str, overwrite: bool = False):
        self.path = path
        self.overwrite = overwrite

    def consume_secrets(self, data: dict) -> bool:
        """
        Write data as `export K=V` pairs into self.path, but die if self.path
        already exists.

        That file can be sourced or evaluated with the unix shell
        """
        if os.path.exists(self.path) and not self.overwrite:
            raise RuntimeError(f'{self.path} already exists')

        with open(self.path, 'w') as secrets_file:
            logger.info(
                f"consuming {self}",
            )

            secrets_file.write(
                "\n".join(
                    util.dict2env(data)
                )
            )
            secrets_file.write('\n')
            


class JsonWriter(Consumer):
    """
    This Consumer will write secrets as a JSON dictionary
    
    >>> JsonWriter('/etc/passwd').consume_secrets({"K":"V"})
    Traceback (most recent call last):
      ...
    RuntimeError: /etc/passwd already exists

    We want the dictionary outputted in the right format:
    >>> JsonWriter('tests/new.json').consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.json').read()
    '{\\n  "K1": "V1",\\n  "K2": "V2"\\n}\\n'

    We may specify to overwrite the destination file
    >>> JsonWriter(
    ...     'tests/new.json', 
    ...     overwrite=True
    ... ).consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.json').read()
    '{\\n  "K1": "V1",\\n  "K2": "V2"\\n}\\n'

    """
    def __init__(self, path: str, overwrite: bool = False):
        self.path = path
        self.overwrite = overwrite

    def __str__(self):
        return f'{self.__class__}->{self.path}'

    def consume_secrets(self, data: dict):
        """
        Write data as json into fname
        That file can be evaluated by any json-aware application.
        """
        if os.path.exists(self.path) and not self.overwrite:
            raise RuntimeError(f'{self.path} already exists')

        with open(self.path, 'w') as json_file:
            logger.info(
                "%s is writing to %s",
                self, self.path
            )

            json.dump(data, json_file, indent=2)
            json_file.write('\n')


class EnvRunner(Consumer):
    """
    This Consumer will update the environment and then run a subprocess in that
    altered environment.
    
    We carry our local environment over into the spawned process:
    >>> os.environ.update({"K1": "V1"})
    >>> EnvRunner('./tests/echo-vars.sh').consume_secrets({"K2":"V2","K3":"V3"})
    K1=V1
    K2=V2
    K3=V3
    
    We fail when the command can not be found:
    >>> EnvRunner('nowhere.sh').consume_secrets({"K1":"V1"})
    Traceback (most recent call last):
    ...
    FileNotFoundError: [Errno 2] No such file or directory: 'nowhere.sh': 'nowhere.sh'
    """
    def __init__(self, path: str):
        self.path = os.environ.get(
            "VAULTIFY_TARGET", path
        ).split()

    def consume_secrets(self, data: dict):
        """
        This consumer does not write a file, but updates its own environment
        with the secret values and calls any subprocess inside that.
        """
        prepared_env = dict(os.environ)

        for key, value in data.items():
            prepared_env.update(
                {key: value}
            )
        logger.info(
            f'{self} enriched the environment')

        try:
            # TODO Overhaul this
            proc = run(
                self.path,
                stdout=PIPE,
                stderr=PIPE,
                env=prepared_env
            )
            logger.info(
                f'running the process "{self.path}"')

        except FileNotFoundError as error:
            logger.critical(
                f'error in {self} executing "{self.path}"')
            raise error

        print(
            proc.stdout.decode()
        )
