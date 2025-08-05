"""API client implementation with robust error handling and monitoring."""

import asyncio
import logging
from typing import AsyncIterator, Dict, Optional

import aiohttp

from src.core.exceptions import APIUnavailableError


class APIClient:
    """Client for interacting with the Llama-GPU API service."""

    def __init__(
        self,
        base_url: str = "http://localhost:8001",
        timeout: int = 30
    ) -> None:
        """Initialize API client.

        Args:
            base_url: Base URL of the API service
            timeout: Default timeout for requests in seconds
        """
        self.base_url = base_url
        self.timeout = timeout
        self.session: Optional[aiohttp.ClientSession] = None
        self.logger = logging.getLogger(__name__)

    async def _ensure_session(self) -> aiohttp.ClientSession:
        """Ensure we have an active session.

        Returns:
            aiohttp.ClientSession: The active session
        """
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=self.timeout)
            )
        return self.session

    async def close(self) -> None:
        """Close the API client session."""
        if self.session and not self.session.closed:
            await self.session.close()

    async def health_check(self) -> Dict:
        """Check API service health.

        Returns:
            Dict: Health check response

        Raises:
            APIUnavailableError: If service is not available
        """
        try:
            session = await self._ensure_session()
            async with session.get(f"{self.base_url}/health") as response:
                if response.status != 200:
                    raise APIUnavailableError(
                        f"Health check failed: {response.status}"
                    )
                return await response.json()
        except Exception as e:
            raise APIUnavailableError(f"Health check error: {str(e)}")

    async def model_status(self) -> Dict:
        """Get model status.

        Returns:
            Dict: Model status information
        """
        session = await self._ensure_session()
        async with session.get(f"{self.base_url}/model/status") as response:
            return await response.json()

    async def chat_completion(
        self,
        message: str,
        stream: bool = True,
        request_id: Optional[str] = None
    ) -> AsyncIterator[Dict]:
        """Send chat completion request.

        Args:
            message: The message to send
            stream: Whether to stream the response
            request_id: Optional request ID for tracking

        Returns:
            AsyncIterator[Dict]: Stream of response chunks
        """
        session = await self._ensure_session()

        payload = {
            "message": message,
            "stream": stream
        }
        if request_id:
            payload["request_id"] = request_id

        headers = {"Accept": "text/event-stream"} if stream else {}

        try:
            async with session.post(
                f"{self.base_url}/v1/chat/completions",
                json=payload,
                headers=headers
            ) as response:
                if stream:
                    async for line in response.content:
                        if line:
                            yield self._parse_stream_line(line)
                else:
                    yield await response.json()
        except Exception as e:
            self.logger.error(f"Chat completion error: {str(e)}")
            raise

    @staticmethod
    def _parse_stream_line(line: bytes) -> Dict:
        """Parse a line from the stream response.

        Args:
            line: Raw line from the stream

        Returns:
            Dict: Parsed response chunk
        """
        try:
            text = line.decode('utf-8').strip()
            if text.startswith('data: '):
                import json
                return json.loads(text[6:])
            return {}
        except Exception as e:
            logging.error(f"Error parsing stream line: {str(e)}")
            return {}
