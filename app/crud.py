#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    crud.py
# @Author:      Kuro
# @Time:        5/21/2025 9:41 AM

from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models import ShortURL


async def create_short_url(db: AsyncSession, *, code: str, original: str) -> ShortURL:
    obj = ShortURL(short_code=code, original_url=original)
    db.add(obj)
    await db.commit()
    await db.refresh(obj)
    return obj


async def get_by_code(db: AsyncSession, code: str) -> ShortURL | None:
    res = await db.execute(select(ShortURL).where(ShortURL.short_code == code))
    return res.scalar_one_or_none()


async def increment_redirect(db: AsyncSession, pk: int):
    record = await db.get(ShortURL, pk)
    if record is None:
        return None  # or raise an exception if preferred
    # Increment the redirect_count
    record.redirect_count += 1

    # Commit changes to the database
    await db.commit()

    # Refresh to get the latest state from the database
    await db.refresh(record)

    # Return the updated record
    return record
