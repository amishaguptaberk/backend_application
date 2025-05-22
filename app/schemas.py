#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    schemas.py
# @Author:      Amisha
# @Time:        5/21/2025 9:40 AM

from datetime import datetime

from pydantic import BaseModel, HttpUrl


class ShortenIn(BaseModel):
    url: HttpUrl


class ShortenOut(BaseModel):
    short_code: str
    short_url: str


class AnalyticsOut(BaseModel):
    short_code: str
    original_url: str
    created_at: datetime
    redirect_count: int
