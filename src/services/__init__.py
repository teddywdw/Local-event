"""
HAR Parsing Service Abstraction Layer

This module provides a clean interface for HAR parsing services that can be
easily swapped between different implementations (local module, API service, etc.)
without breaking the web application code.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Optional, Union
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ParseResult:
    """Standardized result from HAR parsing operations."""

    success: bool
    events: List[Dict] = None
    error_message: str = ""
    event_count: int = 0

    def __post_init__(self):
        if self.success and self.events:
            self.event_count = len(self.events)
        elif not self.success and not self.error_message:
            self.error_message = "Unknown parsing error"


class HarParserService(ABC):
    """Abstract base class defining the HAR parsing service contract."""

    @abstractmethod
    def parse_har_file(
        self, har_file_path: Union[str, Path], debug: bool = False
    ) -> ParseResult:
        """
        Parse a HAR file and return structured event data.

        Args:
            har_file_path: Path to the HAR file to parse
            debug: Enable debug output for troubleshooting

        Returns:
            ParseResult with success status, events list, and any error info
        """
        pass

    @abstractmethod
    def validate_har_file(self, har_file_path: Union[str, Path]) -> bool:
        """
        Validate that a file is a proper HAR file.

        Args:
            har_file_path: Path to the file to validate

        Returns:
            True if file is valid HAR format, False otherwise
        """
        pass

    @abstractmethod
    def get_service_info(self) -> Dict:
        """
        Get information about this parser service implementation.

        Returns:
            Dict with service name, version, capabilities, etc.
        """
        pass


class HarParserFactory:
    """Factory for creating HAR parser service instances based on configuration."""

    _services = {}

    @classmethod
    def register_service(cls, name: str, service_class):
        """Register a parser service implementation."""
        cls._services[name] = service_class

    @classmethod
    def create_parser(cls, service_type: str = "local", **kwargs) -> HarParserService:
        """
        Create a parser service instance.

        Args:
            service_type: Type of service ('local', 'api', 'microservice', etc.)
            **kwargs: Additional arguments for service initialization

        Returns:
            Configured HarParserService instance

        Raises:
            ValueError: If service_type is not registered
        """
        if service_type not in cls._services:
            available = ", ".join(cls._services.keys())
            raise ValueError(
                f"Unknown service type '{service_type}'. Available: {available}"
            )

        service_class = cls._services[service_type]
        return service_class(**kwargs)

    @classmethod
    def list_available_services(cls) -> List[str]:
        """Get list of available service types."""
        return list(cls._services.keys())


# Configuration for service selection
class ParserConfig:
    """Configuration for parser service selection and settings."""

    def __init__(self, service_type: str = "local", **service_kwargs):
        self.service_type = service_type
        self.service_kwargs = service_kwargs

    def create_parser(self) -> HarParserService:
        """Create a parser service using this configuration."""
        return HarParserFactory.create_parser(self.service_type, **self.service_kwargs)


# Import and register available services
from .local_parser import LocalHarParserService
from .api_parser import ApiHarParserService

# Register services with factory
HarParserFactory.register_service("local", LocalHarParserService)
HarParserFactory.register_service("api", ApiHarParserService)

# Default configuration (can be overridden via environment or config file)
DEFAULT_CONFIG = ParserConfig(service_type="local")
