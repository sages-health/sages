#  Copyright (c) 2013-2025. The Johns Hopkins University Applied Physics Laboratory LLC
#
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# NO WARRANTY.   THIS MATERIAL IS PROVIDED "AS IS."  JHU/APL DISCLAIMS ALL
# WARRANTIES IN THE MATERIAL, WHETHER EXPRESS OR IMPLIED, INCLUDING (BUT NOT
# LIMITED TO) ANY AND ALL IMPLIED WARRANTIES OF PERFORMANCE,
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE, AND NON-INFRINGEMENT OF
# INTELLECTUAL PROPERTY RIGHTS. ANY USER OF THE MATERIAL ASSUMES THE ENTIRE
# RISK AND LIABILITY FOR USING THE MATERIAL.  IN NO EVENT SHALL JHU/APL BE
# LIABLE TO ANY USER OF THE MATERIAL FOR ANY ACTUAL, INDIRECT,
# CONSEQUENTIAL, SPECIAL OR OTHER DAMAGES ARISING FROM THE USE OF, OR
# INABILITY TO USE, THE MATERIAL, INCLUDING, BUT NOT LIMITED TO, ANY DAMAGES
# FOR LOST PROFITS.

import argparse
import sys

from argparse import Namespace

from cryptography.fernet import Fernet


def generate(args):
    print(Fernet.generate_key().decode(sys.getdefaultencoding()))


def encrypt(args: Namespace):
    key = Fernet(args.key)
    print(
        key.encrypt(bytes(args.data, sys.getdefaultencoding())).decode(
            sys.getdefaultencoding()
        )
    )


def decrypt(args: Namespace):
    key = Fernet(args.key)
    print(
        key.decrypt(bytes(args.token, sys.getdefaultencoding())).decode(
            sys.getdefaultencoding()
        )
    )


def run():
    root = argparse.ArgumentParser()
    root.set_defaults(func=generate)
    subparsers = root.add_subparsers()

    parser = subparsers.add_parser("generate")
    parser.set_defaults(func=generate)

    parser = subparsers.add_parser("encrypt")
    parser.add_argument("key", help="The encryption key to use")
    parser.add_argument("data", help="The data to encrypt")
    parser.set_defaults(func=encrypt)

    parser = subparsers.add_parser("decrypt")
    parser.add_argument("key", help="The decryption key to use")
    parser.add_argument("token", help="The token to decrypt")
    parser.set_defaults(func=decrypt)

    args = root.parse_args()
    args.func(args)


run()
