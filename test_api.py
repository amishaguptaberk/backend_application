#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    test_api.py

# @Time:        5/21/2025 9:41 AM

import asyncio
import json
import sys

import httpx
import pytest
import websockets
from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


@pytest.mark.asyncio
async def test_shorten_and_redirect():
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        # shorten
        resp = await client.post("/shorten", json={"url": "https://example.com"})
        assert resp.status_code == 201
        data = resp.json()
        assert "short_code" in data

        a = await client.get(f"/analytics/{data['short_code']}")
        assert a.status_code == 200
        assert a.json()["redirect_count"] == 0

        # redirect
        r = await client.get(f"/{data['short_code']}", follow_redirects=False)
        assert r.status_code == 307
        assert r.headers["location"] == "https://example.com/"

        a2 = await client.get(f"/analytics/{data['short_code']}")
        assert a2.json()["redirect_count"] == 1


@pytest.mark.asyncio
async def test_websocket_analytics():
    # Set Windows-compatible event loop policy
    if sys.platform == 'win32':
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    async with httpx.AsyncClient(app=app, base_url="http://test") as client:
        shorten_resp = await client.post("/shorten", json={"url": "https://example.com"})
        assert shorten_resp.status_code == 201, shorten_resp.text
        payload = shorten_resp.json()
        short_code = payload["short_code"]

        ws_url = f"ws://test/analytics/{short_code}"
        async with websockets.connect(ws_url) as websocket:
            initial_data = json.loads(await websocket.recv())
            assert initial_data["short_code"] == short_code
            assert initial_data["redirect_count"] == 0

            redirect_resp = await client.get(f"/{short_code}", follow_redirects=False)
            assert redirect_resp.status_code == 307

            update_data = json.loads(await websocket.recv())
            assert update_data["short_code"] == short_code
            assert update_data["redirect_count"] == 1
