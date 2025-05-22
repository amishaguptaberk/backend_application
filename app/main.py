#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    main.py

# @Time:        5/21/2025 9:41 AM

import os

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, status, WebSocket
from fastapi.responses import RedirectResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.crud import create_short_url, get_by_code, increment_redirect
from app.database import get_db, engine
from app.models import Base
from app.schemas import ShortenIn, ShortenOut, AnalyticsOut
from app.utils import generate_code
from app.websocket_manager import ws_manager

app = FastAPI(title="URL Shortener")


@app.on_event("startup")
async def startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


@app.post("/shorten", response_model=ShortenOut, status_code=201)
async def shorten(in_body: ShortenIn, db: AsyncSession = Depends(get_db)):
    # simple collision-avoid loop
    for _ in range(5):
        new_code = generate_code()
        if await get_by_code(db, new_code) is None:
            record = await create_short_url(db, code=new_code, original=in_body.url)
            short_url = f"{os.getenv('BASE_URL', 'http://localhost:8081')}/{record.short_code}"
            return ShortenOut(short_code=record.short_code, short_url=short_url)

    raise HTTPException(500, "Could not generate unique short code.")


@app.get("/{short_code}")
async def redirect(short_code: str, db: AsyncSession = Depends(get_db)):
    record = await get_by_code(db, short_code)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short code not found")
    updated = await increment_redirect(db, record.id)
    await ws_manager.broadcast(short_code, {"short_code": short_code, "redirect_count": updated.redirect_count})
    return RedirectResponse(updated.original_url, status_code=307)


@app.get("/analytics/{short_code}", response_model=AnalyticsOut)
async def analytics(short_code: str, db: AsyncSession = Depends(get_db)):
    record = await get_by_code(db, short_code)
    if not record:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Short code not found")
    return AnalyticsOut(
        short_code=record.short_code,
        original_url=record.original_url,
        created_at=record.created_at,
        redirect_count=record.redirect_count,
    )


@app.websocket("/ws/analytics/{short_code}")
async def analytics_ws(ws: WebSocket, short_code: str, db: AsyncSession = Depends(get_db)):
    record = await get_by_code(db, short_code)
    if record is None:
        await ws.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await ws_manager.connect(ws)
    await ws_manager.subscribe(ws, short_code)
    try:
        await ws.send_json({"short_code": short_code, "redirect_count": record.redirect_count})
        while True:
            await ws.receive_text()
    except Exception:
        pass
    finally:
        await ws_manager.unsubscribe(ws, short_code)
        await ws_manager.disconnect(ws)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8081)
