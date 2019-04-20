#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import sys

def main():
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        "action", default="run"
    )
    
    parser.add_argument(
        "-v", "--verbosity",
        type=str,
        default='WARN',
        choices=['DEBUG', 'INFO', 'WARN', 'CRIT'],
        help="set logging verbosity"
    )
    
    parser.add_argument(
        '-c', '--config',
        type=argparse.FileType('r'),
        default=sys.stdin,
        help="specify a configuration file to override defaults, if not specified, STDIN will be used"
    )
    
    args = parser.parse_args()
    print(args)
    inp = args.config.read()
    if inp:
        print(inp)
