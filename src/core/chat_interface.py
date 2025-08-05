"""Chat interface implementation with robust error handling and monitoring."""

import asyncio
import logging
import time
from dataclasses import dataclass
from typing import AsyncIterator, Dict, Optional, Union
from uuid import uuid4

from src.core.exceptions import (
    APIUnavailableError,
    ModelNotReadyError,
    RequestTimeoutError,
)


@dataclass
class ChatResponse:
    """Structure for chat response data."""
    message: str
    model_name: str
    request_id: str
    timing: float
    error: Optional[str] = None


class ChatInterface:
    """Robust chat interface with error handling, monitoring and recovery."""

    def __init__(
        self,
        api_client,
        timeout: int = 30,
        max_retries: int = 3,
        retry_delay: float = 1.0
    ):
        """Initialize chat interface.

        Args:
            api_client: API client instance
            timeout: Request timeout in seconds
            max_retries: Maximum number of retry attempts
            retry_delay: Initial delay between retries (with exponential backoff)
        """
        self.api_client = api_client
        self.timeout = timeout
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.logger = logging.getLogger(__name__)

    async def _validate_service(self) -> bool:
        """Check if API service is healthy and model is ready.

        Returns:
            bool: True if service is healthy and ready

        Raises:
            APIUnavailableError: If service is not available
            ModelNotReadyError: If model is not ready
        """
        try:
            health = await self.api_client.health_check()
            if not health['status'] == 'healthy':
                raise APIUnavailableError("API service is not healthy")

            model_status = await self.api_client.model_status()
            if not model_status['ready']:
                raise ModelNotReadyError("Model is not ready")

            return True
        except Exception as e:
            self.logger.error(f"Service validation failed: {str(e)}")
            raise

    async def send_message(
        self,
        message: str,
        stream: bool = True
    ) -> Union[ChatResponse, AsyncIterator[ChatResponse]]:
        """Send message to chat model with error handling and retries.

        Args:
            message: The message to send
            stream: Whether to stream the response

        Returns:
            Union[ChatResponse, AsyncIterator[ChatResponse]]: Response or stream
        """
        request_id = str(uuid4())
        start_time = time.time()
        retry_count = 0
        current_delay = self.retry_delay

        while retry_count <= self.max_retries:
            try:
                # Validate service health
                await self._validate_service()

                # Log request
                self.logger.info(
                    f"Sending message - ID: {request_id}, "
                    f"Length: {len(message)}"
                )

                # Send request with timeout
                response = await asyncio.wait_for(
                    self.api_client.chat_completion(
                        message,
                        stream=stream,
                        request_id=request_id
                    ),
                    timeout=self.timeout
                )

                # Calculate timing
                elapsed = time.time() - start_time

                # Log performance metrics
                logging.getLogger('performance').info(
                    f"request_id={request_id} "
                    f"type=chat_completion "
                    f"duration={elapsed:.3f} "
                    f"status=success"
                )

                if stream:
                    async def response_stream():
                        try:
                            async for chunk in response:
                                yield ChatResponse(
                                    message=chunk['text'],
                                    model_name=chunk['model'],
                                    request_id=request_id,
                                    timing=time.time() - start_time
                                )
                        except Exception as e:
                            self.logger.error(
                                f"Stream error - ID: {request_id}, Error: {str(e)}"
                            )
                            yield ChatResponse(
                                message="",
                                model_name="unknown",
                                request_id=request_id,
                                timing=time.time() - start_time,
                                error=str(e)
                            )
                    return response_stream()
                else:
                    return ChatResponse(
                        message=response['text'],
                        model_name=response['model'],
                        request_id=request_id,
                        timing=elapsed
                    )

            except asyncio.TimeoutError:
                self.logger.warning(
                    f"Request timeout - ID: {request_id}, "
                    f"Attempt: {retry_count + 1}/{self.max_retries}"
                )
                if retry_count == self.max_retries:
                    raise RequestTimeoutError(
                        f"Request timed out after {self.max_retries} attempts"
                    )

            except Exception as e:
                self.logger.error(
                    f"Request failed - ID: {request_id}, "
                    f"Attempt: {retry_count + 1}/{self.max_retries}, "
                    f"Error: {str(e)}"
                )
                if retry_count == self.max_retries:
                    raise

            # Exponential backoff
            await asyncio.sleep(current_delay)
            current_delay *= 2
            retry_count += 1

    async def graceful_shutdown(self) -> None:
        """Gracefully shutdown the chat interface."""
        self.logger.info("Shutting down chat interface")
        try:
            await self.api_client.close()
        except Exception as e:
            self.logger.error(f"Error during shutdown: {str(e)}")
