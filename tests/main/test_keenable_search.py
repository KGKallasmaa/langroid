"""
Tests for Keenable search integration.

Unit tests use mocking and need no network or API key.
The integration test calls the keyless public endpoint.
"""

import os
from unittest.mock import MagicMock, patch

import pytest
import requests

from langroid.agent.tools.keenable_search_tool import KeenableSearchTool
from langroid.parsing.web_search import keenable_search


@pytest.fixture
def mock_keenable_response():
    """Create a mock Keenable API response."""
    response = MagicMock()
    response.json.return_value = {
        "query": "LK-99 superconductor",
        "results": [
            {
                "title": "LK-99 - Wikipedia",
                "url": "https://example.com/page1",
                "description": "",
                "snippet": "LK-99 is a gray-black, polycrystalline compound.",
            },
            {
                "title": "LK-99 research findings",
                "url": "https://example.com/page2",
                "description": "",
                "snippet": "Replication attempts of LK-99 superconductivity.",
            },
        ],
    }
    response.raise_for_status.return_value = None
    return response


class TestKeenableSearchUnit:
    """Unit tests for keenable_search (mocked)."""

    def test_keyless_uses_public_endpoint(self, mock_keenable_response):
        with (
            patch.dict(os.environ, {}, clear=True),
            patch("langroid.parsing.web_search.load_dotenv"),
            patch(
                "langroid.parsing.web_search.requests.post",
                return_value=mock_keenable_response,
            ) as mock_post,
        ):
            results = keenable_search("LK-99 superconductor", num_results=2)

        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.keenable.ai/v1/search/public"
        assert kwargs["headers"]["X-Keenable-Title"] == "langroid"
        assert "X-API-Key" not in kwargs["headers"]
        assert kwargs["json"] == {"query": "LK-99 superconductor", "max_results": 2}

        assert len(results) == 2
        assert results[0].title == "LK-99 - Wikipedia"
        assert results[0].link == "https://example.com/page1"
        assert results[0].full_content == (
            "LK-99 is a gray-black, polycrystalline compound."
        )
        assert results[1].link == "https://example.com/page2"

    def test_api_key_uses_authenticated_endpoint(self, mock_keenable_response):
        with (
            patch.dict(os.environ, {"KEENABLE_API_KEY": "keen_test"}),
            patch(
                "langroid.parsing.web_search.requests.post",
                return_value=mock_keenable_response,
            ) as mock_post,
        ):
            keenable_search("test query", num_results=100)

        args, kwargs = mock_post.call_args
        assert args[0] == "https://api.keenable.ai/v1/search"
        assert kwargs["headers"]["X-API-Key"] == "keen_test"
        assert "X-Keenable-Title" not in kwargs["headers"]
        assert kwargs["json"]["max_results"] == 50

    def test_http_error_raises(self):
        response = MagicMock()
        response.raise_for_status.side_effect = requests.HTTPError("429")
        with (
            patch("langroid.parsing.web_search.requests.post", return_value=response),
            pytest.raises(requests.HTTPError),
        ):
            keenable_search("test query")

    def test_tool_handle(self, mock_keenable_response):
        with patch(
            "langroid.parsing.web_search.requests.post",
            return_value=mock_keenable_response,
        ):
            out = KeenableSearchTool(query="LK-99", num_results=2).handle()
        assert "https://example.com/page1" in out
        assert "LK-99 - Wikipedia" in out


@pytest.mark.skipif(
    os.getenv("KEENABLE_LIVE_TEST") is None,
    reason="set KEENABLE_LIVE_TEST=1 to call the live (keyless) Keenable API",
)
def test_keenable_search_live():
    results = keenable_search("LK-99 superconductor", num_results=3)
    assert 0 < len(results) <= 3
    assert all(r.link and r.link.startswith("http") for r in results)
