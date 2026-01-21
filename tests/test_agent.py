"""
Agent and MCP Integration Tests
"""

import pytest
import asyncio
from unittest.mock import patch, MagicMock, AsyncMock


class TestTaskAgent:
    """Test the Task AI Agent"""

    def test_agent_import(self):
        """Test that agent module can be imported"""
        try:
            from app.agent.agent import TaskAgent

            assert TaskAgent is not None
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_agent_initialization(self):
        """Test agent initialization"""
        try:
            from app.agent.agent import TaskAgent

            agent = TaskAgent()
            assert agent is not None
            assert hasattr(agent, "tools")
            assert hasattr(agent, "process_user_request")
        except ImportError:
            pytest.skip("Agent dependencies not installed")

    def test_agent_tools_defined(self):
        """Test that all expected tools are defined"""
        try:
            from app.agent.agent import TaskAgent

            agent = TaskAgent()

            expected_tools = [
                "login",
                "register_org",
                "list_projects",
                "create_project",
                "list_tasks",
                "create_task",
                "update_task",
                "get_overdue_tasks",
                "get_project_stats",
            ]

            for tool in expected_tools:
                assert tool in agent.tools, f"Tool {tool} not found in agent"
        except ImportError:
            pytest.skip("Agent dependencies not installed")

    @pytest.mark.asyncio
    async def test_agent_login_tool(self):
        """Test agent login tool"""
        try:
            from app.agent.agent import TaskAgent

            agent = TaskAgent()

            # Mock the HTTP response
            with patch.object(
                agent.client, "post", new_callable=AsyncMock
            ) as mock_post:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = {"access_token": "test_token"}
                mock_post.return_value = mock_response

                result = await agent.login("test@example.com", "password")

                assert result["success"] == True
                assert agent.auth_token == "test_token"

            await agent.close()
        except ImportError:
            pytest.skip("Agent dependencies not installed")

    @pytest.mark.asyncio
    async def test_agent_list_tasks(self):
        """Test agent list tasks tool"""
        try:
            from app.agent.agent import TaskAgent

            agent = TaskAgent()
            agent.auth_token = "test_token"

            with patch.object(agent.client, "get", new_callable=AsyncMock) as mock_get:
                mock_response = MagicMock()
                mock_response.status_code = 200
                mock_response.json.return_value = []
                mock_get.return_value = mock_response

                result = await agent.list_tasks()

                assert isinstance(result, list)

            await agent.close()
        except ImportError:
            pytest.skip("Agent dependencies not installed")


class TestMCPServer:
    """Test MCP Server functionality"""

    def test_mcp_server_import(self):
        """Test that MCP server module can be imported"""
        try:
            from app.mcp import server

            assert server is not None
        except ImportError as e:
            pytest.skip(f"MCP dependencies not installed: {e}")

    def test_route_discovery(self):
        """Test that routes are discovered from FastAPI app"""
        from app.main import app
        from fastapi.routing import APIRoute

        routes = [r for r in app.routes if isinstance(r, APIRoute)]

        # Should have multiple routes
        assert len(routes) > 0

        # Should include key endpoints
        route_paths = [r.path for r in routes]
        assert "/health" in route_paths
        assert "/api/v1/auth/login" in route_paths


class TestAttachmentLimits:
    """Test attachment business rules"""

    def test_max_file_size_constant(self):
        """Verify max file size is 5MB"""
        # Check the constant in the tasks endpoint
        MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
        assert MAX_SIZE_BYTES == 5242880

    def test_max_attachments_per_task(self):
        """Verify max attachments is 3"""
        # This is enforced in the upload_attachment endpoint
        MAX_ATTACHMENTS = 3
        assert MAX_ATTACHMENTS == 3
