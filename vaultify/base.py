#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
This file implements the vaultify base class.
"""
import abc
import typing as t
import logging


logger = logging.getLogger(__name__)


class Provider:
    def __str__(self):
        return '{}'.format(self.__class__)

    @abc.abstractmethod
    def get_secrets(self) -> dict:
        pass



class Consumer(metaclass=abc.ABCMeta):
    def __str__(self):
        return '{}'.format(self.__class__)

    @abc.abstractmethod
    def consume_secrets(self,
                        data: dict) -> bool:
        pass


class API(metaclass=abc.ABCMeta):
    """
    ABC meta class for later extensibility
    and cheap NotImplementedErrors
    """
    def __init__(self,
                 provider: Provider,
                 consumer: Consumer):

        self._provider = provider
        self._consumer = consumer

    @abc.abstractmethod
    def validate(self) -> t.Iterable:
        pass

    @abc.abstractmethod
    def get_secrets(self) -> dict:
        pass

    @abc.abstractmethod
    def consume_secrets(self,
                        data: dict) -> bool:
        pass

    @abc.abstractmethod
    def run(self) -> bool:
        pass
