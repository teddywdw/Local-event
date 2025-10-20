"""
API HAR Parser Service Implementation

This service calls a remote API endpoint for HAR parsing.
Perfect for microservice architectures and distributed deployments.
"""

import json
import requests
from pathlib import Path
from typing import Union

from services import HarParserService, ParseResult


class ApiHarParserService(HarParserService):
    """API implementation for remote parser service."""

    def __init__(self, base_url: str, api_key: str = None, timeout: int = 30):
        """
        Initialize the API parser service.

        Args:
            base_url: Base URL of the parser API service
            api_key: Optional API key for authentication
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout = timeout

        # Set up session with common headers
        self.session = requests.Session()
        if api_key:
            self.session.headers.update({"Authorization": f"Bearer {api_key}"})
        self.session.headers.update({"Content-Type": "application/json"})

    def parse_har_file(
        self, har_file_path: Union[str, Path], debug: bool = False
    ) -> ParseResult:
        """Parse HAR file via API call."""
        try:
            # For API implementation, we'd need to:
            # 1. Upload the HAR file or send its contents
            # 2. Call the parse endpoint
            # 3. Handle the response

            # This is a stub implementation - replace with actual API calls
            # when you have a parser microservice deployed

            # Example API structure:
            with open(har_file_path, "r", encoding="utf-8") as f:
                har_content = f.read()

            payload = {"har_content": har_content, "debug": debug, "format": "json"}

            response = self.session.post(
                f"{self.base_url}/api/v1/parse-har", json=payload, timeout=self.timeout
            )

            if response.status_code == 200:
                result_data = response.json()
                return ParseResult(
                    success=True,
                    events=result_data.get("events", []),
                    event_count=result_data.get("event_count", 0),
                )
            else:
                return ParseResult(
                    success=False,
                    error_message=f"API error {response.status_code}: {response.text}",
                )

        except requests.exceptions.Timeout:
            return ParseResult(
                success=False,
                error_message=f"API request timed out after {self.timeout} seconds",
            )
        except requests.exceptions.ConnectionError:
            return ParseResult(
                success=False,
                error_message=f"Could not connect to parser API at {self.base_url}",
            )
        except FileNotFoundError:
            return ParseResult(
                success=False, error_message=f"HAR file not found: {har_file_path}"
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Unexpected error calling parser API: {str(e)}",
            )

    def validate_har_file(self, har_file_path: Union[str, Path]) -> bool:
        """Validate HAR file via API call."""
        try:
            # API endpoint for validation
            with open(har_file_path, "r", encoding="utf-8") as f:
                har_content = f.read()

            response = self.session.post(
                f"{self.base_url}/api/v1/validate-har",
                json={"har_content": har_content},
                timeout=self.timeout,
            )

            if response.status_code == 200:
                return response.json().get("valid", False)
            return False

        except Exception:
            return False

    def get_service_info(self) -> dict:
        """Get information about the API parser service."""
        try:
            response = self.session.get(
                f"{self.base_url}/api/v1/info", timeout=self.timeout
            )

            if response.status_code == 200:
                api_info = response.json()
                api_info.update(
                    {"type": "api", "connection": "remote", "base_url": self.base_url}
                )
                return api_info
            else:
                raise Exception(f"API info request failed: {response.status_code}")

        except Exception as e:
            return {
                "name": "API HAR Parser Service",
                "type": "api",
                "version": "unknown",
                "description": "Remote API parser service (connection failed)",
                "base_url": self.base_url,
                "error": str(e),
                "capabilities": ["parse_facebook_events", "remote_processing"],
                "performance": "Variable (network dependent)",
            }
