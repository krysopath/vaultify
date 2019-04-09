#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This contains some simple util functions used for digesting secrets by
Vaultify
"""
import os
import typing as t
import logging.config
import yaml
from subprocess import Popen


logger = logging.getLogger(__name__)


def dict2env(secret_data: dict) -> t.Iterable:
    """
    This function transforms a dictionary from a vaultify provider and returns
    a list of shell viable lines `export K=v`

    >>> dict2env({"KEY1": "VAL1", "KEY2": "VAL2"})
    ["export KEY1='VAL1'", "export KEY2='VAL2'"]
    """
    logger.debug(
        "transforming this dict to newline separated K=V pairs")
    return [
        f"export { key }='{ value }'"
        for key, value in secret_data.items()
    ]


def env2dict(env_data: t.AnyStr) -> dict:
    """
    This function transforms the data loaded from a file to this
    generalized format:
    {
        "source_filename_A": {"KEY1": "value1", "KEY2": "value2"},
        "...": {...}
    }
    While this is most certainly not necessary, it serves as a
    safeguard against badly formatted input files.

    >>> env2dict('KEY1=VAL1\\nKEY2=VAL2')
    {'KEY1': 'VAL1', 'KEY2': 'VAL2'}
    """
    logger.debug(
        "transforming the env to dict-class")

    dict_data = {}
    line_data = env_data.split('\n')
    for line in line_data:
        if line:
            key, value = line.split('=')
            dict_data[key] = value
    return dict_data


def mask_secrets(secrets: dict) -> dict:
    """
    This function is meant to mask any string values passed between Provider &
    Consumer, if that value is being printed/logged

    >>> mask_secrets({"path": {"secret1": "unreadable", "secret2": "unreadable"}})
    {'path': {'secret1': '******', 'secret2': '******'}}
    """
    logger.debug(
        "hiding secrets for logs")
    masked = {}

    for key, value in secrets.items():
        if not isinstance(value, dict):
            # being extra destructive here, since we do
            # never want secrets leaked into logs
            value = '******'
        elif isinstance(value, dict):
            value = mask_secrets(value)
        else:
            raise ValueError('unforeseen consequences!!!')
        masked[key] = value
    return masked


def run_process(cmd: t.Union[list, tuple],
                kwargs: dict) -> t.AnyStr:
    """
    Run a target process with Popen and kwargs
    :param cmd: for Popen
    :param kwargs: for Popen
    :return: bytes from process stdout

    >>> run_process(
    ...     ['echo', 'something'],
    ...     {'universal_newlines': True, 'encoding': 'utf-8', 'stderr': -1, 'stdout': -1}
    ... )
    'something\\n'
    """
    try:
        proc = Popen(cmd, **kwargs)  # nosec
        proc.wait()
        if proc.returncode:
            # if there is non zero rc, please die
            raise ChildProcessError(
                f'terminated with an non-zero value: {proc.stderr.read()}')

    except OSError as error:
        # this case should handle a missing/non-executable binary
        raise error

    return proc.stdout.read()


def yaml_dict_merge(a: dict, b: dict) -> dict:
    """merges b into a and return merged result

    NOTE: tuples and arbitrary objects are not
    handled as it is totally ambiguous what should happen
    """
    key = None
    try:
        if (a is None
                or isinstance(a, str)
                or isinstance(a, int)
                or isinstance(a, float)
                or isinstance(a, bool)):
            #^ border case for first run or if a is a primitive
            if b:
                # override a only when b has value != None
                a = b
            elif b is False:
                # False overrides a
                a = b
        elif isinstance(a, list):
            # lists should be only appended
            if isinstance(b, list):
                # merge lists
                a.extend(b)
            else:
                # append to list
                a.append(b)
        elif isinstance(a, dict):
            # dicts must be merged
            if isinstance(b, dict):
                for key in b:
                    if key in a:
                        # if they share the key
                        a[key] = yaml_dict_merge(a[key], b[key])
                    else:
                        # or assigned a new value
                        a[key] = b[key]
            else:
                raise ValueError(
                    f'Cannot merge non-dict "{b}" into dict "{a}"')
        else:
            raise NotImplementedError(
                f'Merging "{type(a)}" into "{type(b)}" is not implemented.'
            )
    except TypeError as e:
        raise TypeError(
            f'"{e}" in key "{key}" when merging "{b}" into "{a}"'
        )
    return a


def load_yaml_cfg_sources(yaml_files: t.Iterable) -> list:
    cfg_sources = []
    for config_file in yaml_files:

        if os.path.isfile(config_file):
            with open(config_file) as yaml_conf:
                # linter.run(LINT_CONF, yaml_conf)
                logger.debug(f'reading {config_file}')
                cfg_sources.append(
                    yaml.safe_load(yaml_conf)
                )
        else:
            logger.warning(
                f'file not found: {config_file}'
            )

    return cfg_sources


def prefer_env_if_not_none(key: str) -> t.Union[str, None]:
    return os.environ.get(key, None)



