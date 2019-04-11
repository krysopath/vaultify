#!/usr/bin/env python3
"""
run setup for vaultify
"""
from setuptools import setup

setup(
    name='vaultify',
    packages=['vaultify'],
    version='2.0.0',
    description='A hexagon of secret provisoning',
    author='Georg vom Endt',
    author_email='krysopath@gmail.com',
    url='https://github.com/krysopath/vaultify',
    download_url='https://github.com/author/repo/tarball/2.0.0',
    keywords=['vault', 'gpg', 'secrets', 'docker', 'cli'],
    entry_points={
        'console_scripts': [
            'vaultify=vaultify.vaultify:main',
        ],
    },
    classifiers=[],
)
