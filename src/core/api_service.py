"""API Service implementation with proper initialization and health checks."""

from typing import AsyncIterator, Dict

from fastapi import HTTPException
from fastapi.responses import StreamingResponse

from src.core.exceptions import APIUnavailableError, ModelNotReadyError
from src.core.logging_config import setup_logging

logger = setup_logging(service_name="api-service")


class APIService:
    """Service for handling API requests and model management."""

    def __init__(self):
        """Initialize API service."""
        self.model = None
        self.model_loaded = False
        self.logger = logger

    async def load_model_with_validation(self) -> bool:
        """Load and validate the model.

        Returns:
            bool: True if model loaded successfully

        Raises:
            ModelNotReadyError: If model fails validation
        """
        try:
            # Here you would load your actual model
            # For example:
            # self.model = await ModelManager().load_model("llama-base")
            self.model = await self._load_model()

            # Validate model is responding properly
            test_response = await self.model.generate("test")
            if not test_response:
                msg = "Model validation failed - empty response"
                raise ModelNotReadyError(msg)

            return True
        except Exception as e:
            self.logger.error("Model loading failed: %s", str(e))
            raise ModelNotReadyError(f"Model loading failed: {str(e)}") from e

    async def _load_model(self):
        """Internal method to load model implementation.
        Override this in subclasses with actual model loading logic.
        """
        raise NotImplementedError

    async def startup(self):
        """Initialize and validate API service.

        Raises:
            APIUnavailableError: If service fails to start
        """
        try:
            # Load model with validation
            self.model = await self.load_model_with_validation()
            self.model_loaded = True
            self.logger.info("✅ API service started successfully")
        except (ModelNotReadyError, RuntimeError) as e:
            self.logger.error("❌ API startup failed: %s", str(e))
            raise APIUnavailableError(f"API startup failed: {str(e)}") from e

    async def shutdown(self):
        """Gracefully shutdown the API service."""
        try:
            if self.model:
                # Clean up model resources
                await self.model.unload()
            self.model = None
            self.model_loaded = False
            self.logger.info("API service shutdown complete")
        except (RuntimeError, IOError) as e:
            self.logger.error("Error during shutdown: %s", str(e))

    async def generate_streaming_response(
        self, message: str
    ) -> AsyncIterator[str]:
        """Generate streaming response from the model.

        Args:
            message: Input message to process

        Yields:
            str: Generated tokens
        """
        try:
            async for token in self.model.generate_stream(message):
                yield token
        except RuntimeError as e:
            self.logger.error("Streaming generation failed: %s", str(e))
            raise HTTPException(
                500, f"Streaming generation failed: {str(e)}"
            ) from e

    async def chat_completion(self, message: str, stream: bool = True):
        """Process a chat completion request.

        Args:
            message: Input message to process
            stream: Whether to stream the response

        Returns:
            Response containing generated text or streaming response

        Raises:
            HTTPException: If generation fails
        """
        if not self.model_loaded:
            raise HTTPException(500, "Model not loaded")

        try:
            if stream:
                return StreamingResponse(
                    self.generate_streaming_response(message),
                    media_type="text/plain"
                )
            else:
                response = await self.model.generate(message)
                return {"response": response}
        except RuntimeError as e:
            self.logger.error("Generation failed: %s", str(e))
            raise HTTPException(500, f"Generation failed: {str(e)}") from e

    def health_check(self) -> Dict:
        """Check health status of the API service.

        Returns:
            Dict containing health status information
        """
        return {
            "status": "healthy" if self.model_loaded else "unhealthy",
            "model_loaded": self.model_loaded,
            "service_ready": True
        }
