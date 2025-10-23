"""
Flask web application for HAR Event Parser with service abstraction.
"""

import os
import tempfile
import json
import csv
import io
from datetime import datetime
from pathlib import Path

from flask import (
    Flask,
    request,
    jsonify,
    render_template,
    flash,
    redirect,
    url_for,
    make_response,
    session,
)

# Import the service layer
from services.config import get_config

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-key-change-in-production")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 16MB max file size


def store_result(result):
    """Store parse result in session for downloads."""
    session["last_result"] = {
        "success": result.success,
        "events": result.events,
        "event_count": result.event_count,
        "parse_time_ms": getattr(result, "parse_time_ms", 0),
        "service_used": getattr(result, "service_used", "unknown"),
        "timestamp": datetime.now().isoformat(),
    }


def get_stored_result():
    """Get stored parse result from session."""
    return session.get("last_result")


@app.route("/")
def index():
    """Lincoln Local events page."""
    try:
        # Parse the example HAR file to get events
        example_path = Path(__file__).parent.parent / "parser" / "Example2.har"

        if not example_path.exists():
            # If no example file, show empty page
            return render_template(
                "lincoln_local.html", events=[], error="No events available"
            )

        config = get_config()
        parser = config.create_parser()
        result = parser.parse_har_file(str(example_path), debug=False)

        if result.success and result.events:
            # For now, just get the "Old Fashioned Month at Pour" event
            target_event = None
            for event in result.events:
                if "Old Fashioned" in event.get("name", ""):
                    target_event = event
                    break

            # If we found the target event, show it; otherwise show the first event
            events_to_show = [target_event] if target_event else [result.events[0]]
        else:
            events_to_show = []

        return render_template("lincoln_local.html", events=events_to_show)

    except Exception as e:
        return render_template(
            "lincoln_local.html", events=[], error=f"Error loading events: {str(e)}"
        )


@app.route("/admin")
def admin():
    """Admin upload form page."""
    return render_template("index.html")


@app.route("/upload", methods=["POST"])
def upload_har():
    """Handle HAR file upload and parsing."""
    if "har_file" not in request.files:
        flash("No file selected", "error")
        return redirect(url_for("index"))

    file = request.files["har_file"]
    if file.filename == "":
        flash("No file selected", "error")
        return redirect(url_for("index"))

    if not file.filename.lower().endswith(".har"):
        flash("Please upload a .har file", "error")
        return redirect(url_for("index"))

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".har") as tmp_file:
            file.save(tmp_file.name)

            config = get_config()
            parser = config.create_parser()

            debug = request.form.get("debug") == "1"
            result = parser.parse_har_file(tmp_file.name, debug=debug)

            os.unlink(tmp_file.name)
            store_result(result)

            if result.success:
                flash(f"Successfully parsed {result.event_count} events", "success")
            else:
                flash(f"Parse failed: {result.error_message}", "error")

            return render_template(
                "results.html",
                result=result,
                debug_info=getattr(result, "debug_info", None) if debug else None,
            )

    except Exception as e:
        flash(f"Upload failed: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/parse-example", methods=["POST"])
def parse_example():
    """Parse the example HAR file."""
    try:
        example_path = Path(__file__).parent.parent / "parser" / "Example2.har"

        if not example_path.exists():
            flash("Example HAR file not found", "error")
            return redirect(url_for("index"))

        config = get_config()
        parser = config.create_parser()
        result = parser.parse_har_file(str(example_path), debug=False)

        store_result(result)

        if result.success:
            flash(
                f"Successfully parsed {result.event_count} events from example file",
                "success",
            )
        else:
            flash(f"Parse failed: {result.error_message}", "error")

        return render_template("results.html", result=result)

    except Exception as e:
        flash(f"Example parse failed: {str(e)}", "error")
        return redirect(url_for("index"))


@app.route("/download/json")
def download_json():
    """Download last parse results as JSON."""
    result = get_stored_result()
    if not result or not result["success"]:
        flash("No results available for download", "error")
        return redirect(url_for("index"))

    json_data = json.dumps(result["events"], indent=2)
    response = make_response(json_data)
    response.headers["Content-Type"] = "application/json"
    response.headers["Content-Disposition"] = (
        "attachment; filename=facebook_events.json"
    )
    return response


@app.route("/download/csv")
def download_csv():
    """Download last parse results as CSV."""
    result = get_stored_result()
    if not result or not result["success"]:
        flash("No results available for download", "error")
        return redirect(url_for("index"))

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["Name", "DateTime", "Location", "Details", "Link", "Event ID"])

    for event in result["events"]:
        writer.writerow(
            [
                event["name"],
                event["datetime"],
                event["location"] or "",
                event["details"] or "",
                event["link"],
                event["event_id"],
            ]
        )

    csv_data = output.getvalue()
    output.close()

    response = make_response(csv_data)
    response.headers["Content-Type"] = "text/csv"
    response.headers["Content-Disposition"] = "attachment; filename=facebook_events.csv"
    return response


@app.route("/api/docs")
def api_docs():
    """API documentation page."""
    return render_template("api_docs.html")


@app.route("/api/events/parse", methods=["POST"])
def api_parse_events():
    """API endpoint for parsing HAR files."""
    if "har_file" not in request.files:
        return jsonify({"success": False, "error_message": "No file provided"}), 400

    file = request.files["har_file"]
    if file.filename == "":
        return jsonify({"success": False, "error_message": "No file selected"}), 400

    if not file.filename.lower().endswith(".har"):
        return (
            jsonify(
                {
                    "success": False,
                    "error_message": "Invalid file type. Only .har files are supported",
                }
            ),
            400,
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".har") as tmp_file:
            file.save(tmp_file.name)

            config = get_config()
            parser = config.create_parser()

            debug = request.form.get("debug", "").lower() in ("true", "1", "yes")
            result = parser.parse_har_file(tmp_file.name, debug=debug)

            os.unlink(tmp_file.name)

            return jsonify(
                {
                    "success": result.success,
                    "event_count": result.event_count,
                    "events": result.events,
                    "parse_time_ms": getattr(result, "parse_time_ms", 0),
                    "service_used": getattr(result, "service_used", "unknown"),
                    "error_message": result.error_message,
                    "debug_info": (
                        getattr(result, "debug_info", None) if debug else None
                    ),
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error_message": str(e)}), 500


@app.route("/api/health")
def api_health():
    """API health check endpoint."""
    return jsonify(
        {
            "status": "healthy",
            "service": "HAR Event Parser API",
            "version": "1.0.0",
            "timestamp": datetime.now().isoformat(),
        }
    )


@app.route("/api/info")
def api_info():
    """API service information endpoint."""
    config = get_config()
    parser = config.create_parser()

    return jsonify(
        {
            "service_type": config.service_type,
            "service_info": parser.get_service_info(),
            "supported_formats": [".har"],
            "max_file_size_mb": 16,
            "features": ["facebook_events", "json_output", "debug_mode"],
        }
    )


if __name__ == "__main__":
    app.run(debug=True, port=5000)
