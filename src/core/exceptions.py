"""Custom exceptions for Llama-GPU."""

class LlamaGPUError(Exception):
    """Base exception for Llama-GPU errors."""
    pass


class APIUnavailableError(LlamaGPUError):
    """Raised when the API service is not available."""
    pass


class ModelNotReadyError(LlamaGPUError):
    """Raised when the model is not ready to process requests."""
    pass


class RequestTimeoutError(LlamaGPUError):
    """Raised when a request times out."""
    pass


class ModelError(LlamaGPUError):
    """Raised when there is an error with the model processing."""
    pass


class ConfigurationError(LlamaGPUError):
    """Raised when there is an error in configuration."""
    pass
