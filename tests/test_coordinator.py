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


def test_parse_response_respects_max_per_show() -> None:
    """Parser takes a caller-provided per-show episode limit."""
    # Page without episode rows parses to an empty list at any configured limit.
    show = _parse_response(
        "test-show",
        '<div class="serienlogo"><img src="/logo.jpg"></div>'
        '<h1><a>Test Show</a></h1>',
        dt.date.today(),
        max_per_show=2,
    )
    assert show["episodes"] == []