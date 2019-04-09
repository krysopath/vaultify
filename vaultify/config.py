#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
from pprint import pprint
from .util import yaml_dict_merge, load_yaml_cfg_sources

MODULE_BASE_DIR = os.path.dirname(
    os.path.realpath(__file__))
ETC_DEFAULT_CONFIG = '/etc/default/vaultify.yml'
USER_CONFIG = f'{os.environ.get("HOME")}/.vaultify.yml'
LOCAL_CONFIG = f'{os.environ.get("PWD")}/.vaultify.yml'

CFG_DEFAULT_FILES = [
    ETC_DEFAULT_CONFIG,
    USER_CONFIG,
    LOCAL_CONFIG]


BASE_CFG = {
    "vaultify": {
    },
    "handlers": {
        "console": {
            "level": "DEBUG",
        },
        "file": {
            "level": "DEBUG",
            "filename": "./vaultify.log"
        }
    },
    "loggers": {
    }
}


LOG_CFG = {
    "version": 1,
    "formatters": {
        "simple": {
            "class": "logging.Formatter",
            "format": '[%(levelname)-5.5s] [%(name)-20.20s] - %(message)s'
        },
        "extended": {
            "class": "logging.Formatter",
            "format": "[%(asctime)s] [%(name)-20.20s] [%(levelname)-5.5s]  %(message)s"
        }
    },
    "handlers": {
        "console": {
            "class": "logging.StreamHandler",
            "level": "DEBUG",
            "stream": 'ext://sys.stdout',
            "formatter": "simple"
        },
        "file": {
            "class": "logging.FileHandler",
            "level": "DEBUG",
            "filename": "./debug.log",
            "mode": "w",
            "formatter": "extended"
        }
    },
    "loggers": {
        "": {
            "level": "DEBUG",
            "handlers": ["console", "file"],
            "propagate": True
        },

    }
}


ENV_CFG = {
    "vaultify": {
        "provider": {
            "class": os.environ.get("VAULTIFY_PROVIDER"),
            "args": {
                "secret": os.environ.get("VAULTIFY_SECRET")
            }
        },
        "consumer": {
            "class": os.environ.get("VAULTIFY_CONSUMER"),
            "args": {
                "path": os.environ.get("VAULTIFY_DESTINATION")
            }
        }
    },
    "handlers": {
        "console": {
            "level": os.environ.get("VAULTIFY_LOG_LEVEL"),
        },
        "file": {
            "level": os.environ.get("VAULTIFY_LOG_LEVEL"),
            "filename": os.environ.get("VAULTIFY_LOG_FILE")
        }
    },
    "loggers": {
        "": {
            "level": os.environ.get("VAULTIFY_LOG_LEVEL")
        }
    }
}


def configure(
        yaml_files: list = CFG_DEFAULT_FILES) -> dict:

    """
        This populates a global config dictionary with merged values
    from yaml cfg files.

    :param yaml_files: a list off yaml filenames that could exist
    :return: the final global config dict
    """
    config_data = yaml_dict_merge(LOG_CFG, BASE_CFG)

    cfg_sources = load_yaml_cfg_sources(yaml_files)

    for src in cfg_sources:
        if src:
            config_data = yaml_dict_merge(
                config_data, src
            )

    config_data = yaml_dict_merge(config_data, ENV_CFG)

    return config_data


__all__ = (
    "MODULE_BASE_DIR",
    "ETC_DEFAULT_CONFIG",
    "USER_CONFIG",
    "LOCAL_CONFIG",
    "CFG_DEFAULT_FILES",
    "BASE_CFG",
    "LOG_CFG"
)