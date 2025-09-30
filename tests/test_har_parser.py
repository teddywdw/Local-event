from pathlib import Path
import json

from src.har_parser import parse_facebook_har


def test_parse_happy_path(tmp_path):
    fixtures = Path(__file__).resolve().parents[0] / "fixtures"
    sample = fixtures / "simple.har"
    assert sample.exists()
    events = parse_facebook_har(str(sample))
    assert isinstance(events, list)
    assert "Test Event" in events


def test_parse_no_graphql(tmp_path):
    # create a minimal HAR with no graphql entries
    no_graph = tmp_path / "no_graph.har"
    no_graph.write_text('{"log": {"entries": []}}', encoding="utf-8")
    events = parse_facebook_har(str(no_graph))
    assert events == []


def test_parse_concatenated_json(tmp_path):
    # build a HAR where the response.text is two JSON objects separated by newline
    har = {
        "log": {
            "version": "1.2",
            "creator": {"name": "test", "version": "1.0"},
            "entries": [
                {
                    "request": {
                        "method": "POST",
                        "url": "https://www.facebook.com/api/graphql/",
                    },
                    "response": {
                        "content": {
                            "text": '{"data": {"node": {"__typename": "Event", "name": "Event A"}}}\n{"data": {"node": {"__typename": "Event", "name": "Event B"}}}'
                        }
                    },
                }
            ],
        }
    }

    p = tmp_path / "concat.har"
    p.write_text(json.dumps(har), encoding="utf-8")
    events = parse_facebook_har(str(p))
    assert isinstance(events, list)
    assert "Event A" in events
    assert "Event B" in events
