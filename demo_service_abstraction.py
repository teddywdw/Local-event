#!/usr/bin/env python3
"""
Demonstration of HAR Parser Service Abstraction

This script shows how the web application can use different parser
implementations without changing any code - just configuration.
"""

import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.services import ParserConfig
from src.services.config import get_config


def demo_service_switching():
    """Demonstrate switching between different parser services."""

    print("=== HAR Parser Service Abstraction Demo ===\n")

    # Test HAR file path
    test_har_file = "src/parser/Example2.har"

    if not Path(test_har_file).exists():
        print(f"ERROR: Test HAR file not found: {test_har_file}")
        return

    # Demo 1: Using local service directly
    print("1. Using Local Parser Service")
    print("-" * 40)

    local_config = ParserConfig(service_type="local")
    local_parser = local_config.create_parser()

    print(f"Service Info: {local_parser.get_service_info()['name']}")

    # Parse with local service
    result = local_parser.parse_har_file(test_har_file, debug=False)

    if result.success:
        print(f"✅ Successfully parsed {result.event_count} events")
        print(f"   First event: {result.events[0]['name']}")
    else:
        print(f"❌ Parsing failed: {result.error_message}")

    print()

    # Demo 2: Show how easy it is to switch to API service (would fail with stub)
    print("2. API Service Configuration (Stub - Will Fail Gracefully)")
    print("-" * 60)

    # This would work if you had an API service running
    api_config = ParserConfig(
        service_type="api", base_url="http://localhost:8080", timeout=10
    )

    try:
        api_parser = api_config.create_parser()
        print(f"Service Info: {api_parser.get_service_info()['name']}")

        # This will fail gracefully since no API is running
        result = api_parser.parse_har_file(test_har_file, debug=False)

        if result.success:
            print(f"✅ Successfully parsed {result.event_count} events")
        else:
            print(f"❌ Expected failure (no API running): {result.error_message}")

    except Exception as e:
        print(f"❌ Service creation failed: {e}")

    print()

    # Demo 3: Show environment-based configuration
    print("3. Environment-Based Configuration")
    print("-" * 40)

    # Set environment variable for demo
    os.environ["HAR_PARSER_SERVICE"] = "local"

    env_config = get_config()
    env_parser = env_config.create_parser()

    print(f"Service from environment: {env_parser.get_service_info()['name']}")

    result = env_parser.parse_har_file(test_har_file, debug=False)

    if result.success:
        print(f"✅ Successfully parsed {result.event_count} events")
    else:
        print(f"❌ Parsing failed: {result.error_message}")

    print()

    # Demo 4: Show validation
    print("4. HAR File Validation")
    print("-" * 30)

    parser = local_config.create_parser()

    # Valid HAR file
    is_valid = parser.validate_har_file(test_har_file)
    print(f"✅ {test_har_file} is valid: {is_valid}")

    # Invalid file (if exists)
    invalid_file = "README.md"
    if Path(invalid_file).exists():
        is_valid = parser.validate_har_file(invalid_file)
        print(f"❌ {invalid_file} is valid: {is_valid}")

    print()

    # Summary
    print("=== Summary ===")
    print("The abstraction layer allows you to:")
    print("  • Switch parser implementations without changing web app code")
    print("  • Use environment variables or config files for deployment flexibility")
    print("  • Add new service types (database, cloud APIs, etc.) easily")
    print("  • Maintain consistent error handling across all implementations")
    print("  • Test with different services during development")
    print("\nFor production, you could:")
    print("  • Deploy parser as microservice and use 'api' service type")
    print("  • Use 'local' for development and testing")
    print("  • Switch via single environment variable: HAR_PARSER_SERVICE=api")


def show_web_app_usage():
    """Show how a web app would use this abstraction."""

    print("\n=== Web Application Usage Example ===\n")

    example_code = """
# In your Flask/FastAPI web app - NO changes needed when switching services!

from src.services.config import get_config

# Get parser service (local/api/microservice based on config)
config = get_config()
parser = config.create_parser()

@app.route('/upload-har', methods=['POST'])
def upload_har():
    har_file_path = save_uploaded_file()

    # Parse HAR - same code works with ANY service implementation
    result = parser.parse_har_file(har_file_path, debug=False)

    if result.success:
        # Store in database
        store_events_in_db(result.events)
        return {"message": f"Processed {result.event_count} events"}
    else:
        return {"error": result.error_message}, 400

# Switch services by changing ONLY configuration:
# Local dev:       HAR_PARSER_SERVICE=local
# Production API:  HAR_PARSER_SERVICE=api HAR_PARSER_API_URL=https://api.com
"""

    print(example_code)


if __name__ == "__main__":
    demo_service_switching()
    show_web_app_usage()
