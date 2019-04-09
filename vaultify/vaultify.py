#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
This file implements vaultifys main function
"""

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
    """

    def get_secrets(self) -> dict:
        logger.info(
            f'providing secrets from {self._provider}',
        )
        return self._provider.get_secrets()

    def consume_secrets(self,
                        data: dict) -> bool:
        logger.info(
            f'consuming secrets with {self._consumer}'
        )
        return self._consumer.consume_secrets(data)

    def validate(self) -> t.Iterable:
        results = []
        if not isinstance(self._provider,
                          Provider):
            results.append(
                ProviderError(
                    f"The Provider {self._provider} is not a Provider"
                )
            )
        if not isinstance(self._consumer,
                          Consumer):
            results.append(
                ConsumerError(
                    f"The Consumer {self._consumer} is not a Consumer"
                )
            )

        return results

    def run(self) -> bool:
        secrets = self.get_secrets()
        if not secrets:
            raise ValueError(
                f'The provider did not yield anything: {self._provider}'
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
    vaultify = factory(CFG)
    vaultify.validate()
    vaultify.run()


