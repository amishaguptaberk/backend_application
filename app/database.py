#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    database.py
# @Author:      Amisha
# @Time:        5/21/2025 9:40 AM

import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker

load_dotenv()

ASYNC_DB_URL = os.getenv("ASYNC_DB_URL", "mysql+aiomysql://root:root@db:3306/url_shortener")
engine = create_async_engine(ASYNC_DB_URL, pool_pre_ping=True, pool_recycle=3600)
AsyncSessionLocal = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
