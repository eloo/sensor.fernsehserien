"""Tests for deterministic episode parsing."""

import datetime as dt

from custom_components.fernsehserien.coordinator import _parse_response


def test_parse_response_rejects_unrecognized_page() -> None:
    """Unexpected website structure fails clearly."""
    try:
        _parse_response("test-show", "<html></html>", dt.date.today())
    except ValueError as err:
        assert "Serienlogo" in str(err)
    else:
        raise AssertionError("Expected malformed page to fail parsing")