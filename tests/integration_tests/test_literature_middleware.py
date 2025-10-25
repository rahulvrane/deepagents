"""Integration tests for LiteratureSearchMiddleware."""

import pytest
from langchain_core.messages import HumanMessage

from deepagents import create_deep_agent
from deepagents.middleware.scientific import LiteratureSearchMiddleware


class TestLiteratureSearchMiddleware:
    """Tests for literature search middleware."""

    def test_create_middleware(self):
        """Test middleware creation."""
        middleware = LiteratureSearchMiddleware()
        assert middleware is not None
        assert len(middleware.tools) > 0

    def test_middleware_with_agent(self):
        """Test middleware integration with agent."""
        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()]
        )
        assert agent is not None

        # Check that literature search tools are available
        tool_names = set(agent.nodes["tools"].bound._tools_by_name.keys())
        assert "search_pubmed" in tool_names
        assert "search_arxiv" in tool_names
        assert "search_semantic_scholar" in tool_names

    def test_custom_tool_selection(self):
        """Test enabling/disabling specific tools."""
        # Only PubMed enabled
        middleware = LiteratureSearchMiddleware(
            enable_pubmed=True,
            enable_arxiv=False,
            enable_semantic_scholar=False,
            enable_pdf_download=False,
            enable_pdf_parsing=False,
        )

        tool_names = {tool.name for tool in middleware.tools}
        assert "search_pubmed" in tool_names
        assert "search_arxiv" not in tool_names
        assert "search_semantic_scholar" not in tool_names

    @pytest.mark.skipif(
        not pytest.config.getoption("--run-api-tests", default=False),
        reason="API tests disabled by default. Use --run-api-tests to enable."
    )
    def test_pubmed_search_integration(self):
        """Test PubMed search through agent (requires API access)."""
        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()]
        )

        result = agent.invoke({
            "messages": [
                HumanMessage(
                    content="Search PubMed for papers about CRISPR. Just find 2 papers and list their titles."
                )
            ]
        })

        # Verify agent attempted to use search tool
        messages = result.get("messages", [])
        tool_calls = [
            tc
            for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        assert any("pubmed" in tc["name"].lower() for tc in tool_calls)

    @pytest.mark.skipif(
        not pytest.config.getoption("--run-api-tests", default=False),
        reason="API tests disabled by default"
    )
    def test_arxiv_search_integration(self):
        """Test arXiv search through agent."""
        agent = create_deep_agent(
            middleware=[LiteratureSearchMiddleware()]
        )

        result = agent.invoke({
            "messages": [
                HumanMessage(
                    content="Search arXiv for papers about machine learning. Find 2 recent papers."
                )
            ]
        })

        messages = result.get("messages", [])
        tool_calls = [
            tc
            for msg in messages
            if hasattr(msg, "tool_calls")
            for tc in msg.tool_calls
        ]

        assert any("arxiv" in tc["name"].lower() for tc in tool_calls)
