#!/usr/bin/env python3

import unittest
import doctest
import os

files = []
root_dir = 'vaultify/'

for root, _, filenames in os.walk(root_dir):
     for filename in filenames:
          if (filename == '__init__.py'
                or filename[-3:] != '.py'
                or filename.startswith('.#')
          ):
            continue
          f = os.path.join(root, filename)
          f = f.replace('/', '.')
          f = f[:-3]
          files.append(f)

suite = unittest.TestSuite()
for module in files:
    suite.addTest(doctest.DocTestSuite(module))

results = unittest.TextTestRunner(verbosity=1).run(suite)
if any([results.failures, results.errors]):
    num = len(results.failures) + len(results.errors)
    exit(num)
