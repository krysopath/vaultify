#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file implements vaultifys main function
"""

import sys
import logging
import typing as t

from . import CFG
from .base import API, Consumer, Provider
from .util import mask_secrets
from .exceptions import ProviderError, ConsumerError


logger = logging.getLogger(__name__)


class Vaultify(API):
    """
    This is the Vaultify implementation that runs our domain logic

    >>> Vaultify()
    Traceback (most recent call last):
      ...
    TypeError: __init__() missing 2 required positional arguments: 'provider' and 'consumer'

    >>> from . import consumers, providers
    >>> vfy = Vaultify(
    ...     consumer=consumers.EnvRunner('env'), 
    ...     provider=providers.GPGProvider('abc')
    ... )
    >>> isinstance(vfy, Vaultify)
    True

    """

    def get_secrets(self) -> dict:
        logger.info(
            'providing secrets from {}'.format(
                self._provider)
        )
        return self._provider.get_secrets()

    def consume_secrets(self,
                        data: dict) -> bool:
        logger.info(
            'consuming secrets with {}'.format(
                self._consumer)
        )
        return self._consumer.consume_secrets(data)

    def validate(self) -> t.Iterable:
        """
        >>> vfy = Vaultify(
        ...     consumer="fancystring", 
        ...     provider={1: 2}
        ... )
        >>> isinstance(vfy.validate(), list)
        True
        >>> 
        """

        results = []
        if not isinstance(self._provider,
                          Provider):
            results.append(
                ProviderError(
                    "The Provider {} is not a Provider".format(
                        self._provider)
                )
            )
        if not isinstance(self._consumer,
                          Consumer):
            results.append(
                ConsumerError(
                    "The Consumer {} is not a Consumer".format(
                        self._consumer)
                )
            )

        return results

    def run(self) -> bool:
        secrets = self.get_secrets()
        if not secrets:
            raise ValueError(
                'The provider did not yield anything: {}'.format(
                    self._provider)
            )

        to_consumer = {}
        for data in secrets.values():
            logger.info(
                'consuming secret: %s',
                mask_secrets(secrets)
                )
            to_consumer.update(data)

        return self.consume_secrets(to_consumer)


def factory(config_dict: dict, **kwargs) -> Vaultify:
    """
    This implements a Vaultify factory, creating
    a usable vaultify instance
    :param config_dict: an initialised cfg dict
    :param kwargs: user passed kwargs
    :return:
 
    >>> from . import configure
    >>> isinstance(
    ...     factory(configure()), 
    ...     Vaultify
    ... )
    True

    """
    logger.debug("factory starting..")
    vfy = config_dict['vaultify']

    from . import providers
    from . import consumers

    provider_class = getattr(
            providers,
            vfy["provider"]["class"]
        )
    consumer_class = getattr(
        consumers,
        vfy["consumer"]["class"]
    )

    return Vaultify(
        provider=provider_class(**vfy["provider"]["args"]),
        consumer=consumer_class(**vfy["consumer"]["args"])
        )


def main() -> None:
    """
    Yes this is the main function. It creates an instance of the
    vaultify domain logic class, runs it. Very main()
    """
    print(sys.argv)
    vaultify = factory(CFG)
    vaultify.validate()
    vaultify.run()


