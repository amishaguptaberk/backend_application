#!/usr/bin/env python
# -*- coding:utf-8 -*-
# @Filename:    websocket_manager.py
# @Author:      Kuro
# @Time:        5/21/2025 9:41 AM

from asyncio import Lock
from collections import defaultdict
from typing import Dict, Set

from fastapi import WebSocket


class WSManager:
    """
    Tracks connections per short_code.
    """

    def __init__(self):
        self.websocket_topics: Dict[WebSocket, Set[str]] = defaultdict(set)
        self.topic_websockets: Dict[str, Set[WebSocket]] = defaultdict(set)
        self._lock = Lock()

    async def connect(self, ws: WebSocket):
        """
        Accept a new WebSocket connection. This doesn't automatically
        subscribe it to a short code.
        """
        await ws.accept()

    async def subscribe(self, ws: WebSocket, short_code: str):
        """
        Subscribes the given WebSocket connection to the specified short code.
        """
        async with self._lock:
            self.websocket_topics[ws].add(short_code)
            self.topic_websockets[short_code].add(ws)

    async def unsubscribe(self, ws: WebSocket, short_code: str):
        """
        Unsubscribes the given WebSocket from a specific short code.
        """
        async with self._lock:
            self.websocket_topics[ws].discard(short_code)
            self.topic_websockets[short_code].discard(ws)
            if not self.topic_websockets[short_code]:
                del self.topic_websockets[short_code]

    async def disconnect(self, ws: WebSocket):
        """
        Disconnect the given WebSocket from all short codes it is subscribed to.
        """
        async with self._lock:
            # Remove from each short code collection
            subscribed_codes = self.websocket_topics[ws]
            for short_code in subscribed_codes:
                self.topic_websockets[short_code].discard(ws)
                if not self.topic_websockets[short_code]:
                    del self.topic_websockets[short_code]
            # Remove it from the global map
            del self.websocket_topics[ws]

    async def broadcast(self, short_code: str, message: dict):
        """
        Sends a JSON message to all WebSockets subscribed to the given short code.
        Automatically removes any broken connections.
        """
        async with self._lock:
            if short_code not in self.topic_websockets:
                return

            to_remove = []
            for ws in self.topic_websockets[short_code]:
                try:
                    await ws.send_json(message)
                except Exception:
                    # Mark connection for removal
                    to_remove.append(ws)

            # Clean up any broken connections
            for broken_ws in to_remove:
                await self.disconnect(broken_ws)


ws_manager = WSManager()
