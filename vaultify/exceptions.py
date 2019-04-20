#!/usr/bin/env python3
# -*- coding: utf-8 -*-


class ValidationError(Exception):
    def __str___(self):
        return "{} did not validate successfully".format(self.args)

    """
    Serves as the common base class for vaultify validation problems.
    """
    pass


class VaultifyEnvironmentError(ValidationError):
    """
    Raise this when any vaultify environment variable is unset.
    """

    pass


class AdapterValidationError(ValidationError):
    """
    Raise this when any vaultify adapter is misconfigured
    """

    pass


class ProviderError(AdapterValidationError):
    """
    Raise this when a Provider is misconfigured
    """

    pass


class ConsumerError(AdapterValidationError):
    """
    Raise this when a Consumer is misconfigured
    """

    pass
