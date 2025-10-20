"""
Local HAR Parser Service Implementation

This service wraps the local parser module for use in the abstraction layer.
Perfect for local development and single-instance deployments.
"""

import json
from pathlib import Path
from typing import Union

from services import HarParserService, ParseResult
from parser import main as parse_har_main


class LocalHarParserService(HarParserService):
    """Local implementation using the direct parser module."""

    def __init__(self, parser_module_path: str = None):
        """
        Initialize the local parser service.

        Args:
            parser_module_path: Optional custom path to parser module (for testing)
        """
        self.parser_module_path = parser_module_path

    def parse_har_file(
        self, har_file_path: Union[str, Path], debug: bool = False
    ) -> ParseResult:
        """Parse HAR file using the local parser module."""
        try:
            har_path = str(har_file_path)

            # Call the parser module directly
            events = parse_har_main(
                debug=debug, har_path=har_path, output_format="json"
            )

            if events is None:
                return ParseResult(
                    success=False, error_message=f"Failed to parse HAR file: {har_path}"
                )

            return ParseResult(success=True, events=events, event_count=len(events))

        except FileNotFoundError:
            return ParseResult(
                success=False, error_message=f"HAR file not found: {har_file_path}"
            )
        except json.JSONDecodeError as e:
            return ParseResult(
                success=False, error_message=f"Invalid JSON in HAR file: {str(e)}"
            )
        except Exception as e:
            return ParseResult(
                success=False,
                error_message=f"Unexpected error parsing HAR file: {str(e)}",
            )

    def validate_har_file(self, har_file_path: Union[str, Path]) -> bool:
        """Validate HAR file format."""
        try:
            path = Path(har_file_path)

            # Check file exists and has reasonable size
            if not path.exists():
                return False

            if path.stat().st_size == 0:
                return False

            # Try to load as JSON and check for HAR structure
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Basic HAR structure validation
            if not isinstance(data, dict):
                return False

            if "log" not in data:
                return False

            log = data["log"]
            if not isinstance(log, dict):
                return False

            # Check for required HAR fields
            required_fields = ["version", "entries"]
            for field in required_fields:
                if field not in log:
                    return False

            return True

        except (json.JSONDecodeError, IOError, KeyError):
            return False
        except Exception:
            return False

    def get_service_info(self) -> dict:
        """Get information about this local parser service."""
        return {
            "name": "Local HAR Parser Service",
            "type": "local",
            "version": "1.0.0",
            "description": "Direct integration with local parser module",
            "capabilities": [
                "parse_facebook_events",
                "timezone_conversion",
                "json_output",
                "debug_mode",
            ],
            "dependencies": ["src.parser"],
            "performance": "High (no network overhead)",
        }
