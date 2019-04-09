#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import unittest
import hvac
from .util import dict2env
import os

VAULT_ADDR = os.environ.get("VAULT_ADDR", 'http://localhost:8200')
VAULTIFY_TEST_TOKEN = os.environ.get("VAULT_TOKEN", None)

client = hvac.Client(
    url=VAULT_ADDR,
    token=VAULTIFY_TEST_TOKEN
)


class UtilTest(unittest.TestCase):

    def test_vaultify_token_lookup_self(self):
        out = client.lookup_token()
        self.assertTrue("data" in out)

    def test_dict2env(self):
        result = dict2env({
            "KEY1": "ValueAAA",
            "KEY2": "ValueBBB"
        })
        self.assertTrue(isinstance(result, list))
        for item in result:
            k, v = item.split("=")
            if k == "KEY1":
                self.assertTrue(v == "'ValueAAA'")
            elif k == "KEY2":
                self.assertTrue(v == "'ValueBBB'")

    def test_pathReader(self):
        for name, secret in pathReader(
                client,
                ["secret/services/shared/env"]):
            self.assertTrue(name == "env")
            self.assertTrue(secret["CROWDIN_PROJECT_ID"] == "3yourmind")


