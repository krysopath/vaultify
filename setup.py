#!/usr/bin/env python3
"""
run setup for vaultify
"""
from setuptools import setup

setup(
    name="vaultify",
    packages=["vaultify"],
    version="0.1.2",
    description="A hexagon of secret provisoning",
    author="Georg vom Endt",
    author_email="krysopath@gmail.com",
    url="https://github.com/krysopath/vaultify",
    download_url="https://github.com/krysopath/vaultify/tarball/0.1.1",
    keywords=["vault", "gpg", "secrets", "docker", "cli"],
    entry_points={"console_scripts": ["vaultify=vaultify.vaultify:main"]},
    classifiers=[],
)
