#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    models.py
# @Author:      Amisha
# @Time:        5/21/2025 9:40 AM

from sqlalchemy import String, Integer, DateTime, func, Column
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


class ShortURL(Base):
    __tablename__ = "short_urls"
    id = Column(Integer, primary_key=True, index=True)
    short_code = Column(String(10), unique=True, nullable=False)
    original_url = Column(String(2048), nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    redirect_count = Column(Integer, default=0)
