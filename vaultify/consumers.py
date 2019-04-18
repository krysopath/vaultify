#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements Vaultify Consumer classes:

"""

import logging
import typing as t
import os
import yaml
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


class FileWriter:
    """
    instantiate a FileWriter:
    >>> fw = FileWriter('tests/new.filewriter', mode=0o600, overwrite=False)
    >>> isinstance(fw, FileWriter)
    True
    """
    def __init__(self,
                 path: str,
                 mode: oct = 0o600,
                 overwrite: bool = False,
                 *args, **kwargs):
        self.path = path
        self.mode = mode
        self.overwrite = overwrite

    def _write_data_to_fd(self, data: str):
        with open(os.open(self.path,
                          os.O_CREAT | os.O_WRONLY,
                          0o200), 'w') as file_out:
            logger.info(
                "writing to {}, mode {}".format(
                    self.path, oct(self.mode)))
            
            file_out.write(data)
            file_out.write('\n')
        
    def write(self, data: str):
        """
        >>> fw = FileWriter('tests/new.filewriter', overwrite=False)
        >>> fw.write('abc')
        >>> open('tests/new.filewriter', 'r').read()
        'abc\\n'
        >>> fw = FileWriter('tests/new.filewriter', overwrite=True)
        >>> fw.write('def')
        >>> open('tests/new.filewriter', 'r').read()
        'def\\n'
        >>> fw = FileWriter('tests/new.filewriter', overwrite=False)
        >>> fw.write('ghj')
        >>> open('tests/new.filewriter', 'r').read()
        'def\\n'
        """
        if not os.path.exists(self.path):
            self._write_data_to_fd(data)
        else:
            if self.overwrite:
                logger.warning(
                    'overwriting {}'.format(self.path))
                self._write_data_to_fd(data)
            else:
                logger.warning(
                    '{} already exists: skip'.format(
                        self.path))
                
        os.chmod(
            self.path, self.mode)


class DotEnvWriter(Consumer, FileWriter):
    """
    This Consumer writes secrets as a set of sourceable `export KEY=value`
    lines

    We want the dictionary outputted in the right format:
    >>> DotEnvWriter('tests/new.env', overwrite=True).consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.env').read()
    "export K1='V1'\\nexport K2='V2'\\n"
    """
    def consume_secrets(self, data: dict):
        self.write(
            "\n".join(
                util.dict2env(data)))
        

class JsonWriter(Consumer, FileWriter):
    """
    This Consumer writes secrets as a JSON dictionary

    We want the dictionary outputted in the right format:
    >>> JsonWriter('tests/new.json', overwrite=True).consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.json').read()
    '{\\n  "K1": "V1",\\n  "K2": "V2"\\n}\\n'
    """
    def consume_secrets(self, data: dict):
        self.write(json.dumps(
            data,
            sort_keys=True,
            indent=2)
        )
        
class YamlWriter(Consumer, FileWriter):
    """
    This Consumer writes secrets as a YAML dictionary

    We want the dictionary outputted in the right format:
    >>> YamlWriter('tests/new.yaml', overwrite=True).consume_secrets({"K1":"V1","K2":"V2"})
    >>> open('tests/new.yaml').read()
    'K1: V1\\nK2: V2\\n\\n'
    """
    def consume_secrets(self, data: dict):
        self.write(yaml.dump(
            data,
            default_flow_style=False,
            allow_unicode=True,
            encoding='utf-8').decode()
        )


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
            '{} enriched the environment'.format(self))

        try:
            # TODO Overhaul this
            proc = run(
                self.path,
                stdout=PIPE,
                stderr=PIPE,
                env=prepared_env
            )
            logger.info(
                'running the process "{}"'.format(self.path))

        except FileNotFoundError as error:
            logger.critical(
                'error in {} executing "{}"'.format(self, self.path)
            )
            raise error

        print(
            proc.stdout.decode()
        )
