#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    utils.py

# @Time:        5/21/2025 9:41 AM

import random
import string


def generate_code(length: int = 6) -> str:
    alphabet = string.ascii_letters + string.digits
    return "".join(random.choices(alphabet, k=length))

