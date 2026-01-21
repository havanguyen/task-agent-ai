"""
Comprehensive Tests for MCP Server and Agent
"""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
import asyncio


class TestMCPServer:
    """Test MCP Server module"""

    def test_mcp_server_imports(self):
        """Test MCP server module imports"""
        pytest.skip("MCP server requires fastmcp package")

    def test_mcp_has_app_import(self):
        """Test MCP server can access FastAPI app"""
        from app.main import app
        from fastapi.routing import APIRoute

        routes = [r for r in app.routes if isinstance(r, APIRoute)]
        assert len(routes) > 5  # Should have multiple routes

    def test_route_paths_available(self):
        """Test expected route paths exist"""
        from app.main import app
        from fastapi.routing import APIRoute

        route_paths = [r.path for r in app.routes if isinstance(r, APIRoute)]

        # Check core endpoints exist
        assert "/health" in route_paths
        assert "/api/v1/auth/login" in route_paths
        assert "/api/v1/tasks/" in route_paths
        assert "/api/v1/projects/" in route_paths
        assert "/api/v1/users/" in route_paths
        assert "/api/v1/notifications/" in route_paths

    def test_route_methods(self):
        """Test routes have correct HTTP methods"""
        from app.main import app
        from fastapi.routing import APIRoute

        routes = {r.path: r.methods for r in app.routes if isinstance(r, APIRoute)}

        # Login should be POST
        assert "POST" in routes.get("/api/v1/auth/login", set())

        # Health check should be GET
        assert "GET" in routes.get("/health", set())


class TestAgentModule:
    """Test Agent module"""

    def test_agent_imports(self):
        """Test agent module imports"""
        from app.agent import agent

        assert agent is not None

    def test_task_agent_class(self):
        """Test TaskAgent class exists"""
        from app.agent.agent import TaskAgent

        assert TaskAgent is not None

    def test_agent_has_tools(self):
        """Test agent has tools defined"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        assert hasattr(agent, "tools")
        assert isinstance(agent.tools, dict)
        assert len(agent.tools) > 0

    def test_agent_tool_names(self):
        """Test expected tool names exist"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        expected_tools = [
            "login",
            "list_projects",
            "list_tasks",
            "create_task",
            "update_task",
        ]

        for tool_name in expected_tools:
            assert tool_name in agent.tools

    def test_agent_headers_method(self):
        """Test _headers method"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        headers = agent._headers()
        assert "Content-Type" in headers
        assert headers["Content-Type"] == "application/json"

    def test_agent_headers_with_token(self):
        """Test _headers method with auth token"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token_123"

        headers = agent._headers()
        assert "Authorization" in headers
        assert headers["Authorization"] == "Bearer test_token_123"

    def test_agent_tool_descriptions(self):
        """Test tool descriptions exist"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        assert hasattr(agent, "tool_descriptions")
        assert "login" in agent.tool_descriptions.lower()
        assert "task" in agent.tool_descriptions.lower()

    @pytest.mark.asyncio
    async def test_login_tool_mock(self):
        """Test login tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"access_token": "mock_token"}
            mock_post.return_value = mock_response

            result = await agent.login("test@example.com", "password123")

            assert result["success"] is True
            assert agent.auth_token == "mock_token"

        await agent.close()

    @pytest.mark.asyncio
    async def test_login_tool_failure(self):
        """Test login tool handles failure"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 401
            mock_response.text = "Unauthorized"
            mock_post.return_value = mock_response

            result = await agent.login("test@example.com", "wrongpass")

            assert result["success"] is False

        await agent.close()

    @pytest.mark.asyncio
    async def test_list_projects_mock(self):
        """Test list_projects tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = [{"id": 1, "name": "Test Project"}]
            mock_get.return_value = mock_response

            result = await agent.list_projects()

            assert isinstance(result, list)
            assert len(result) == 1

        await agent.close()

    @pytest.mark.asyncio
    async def test_list_tasks_mock(self):
        """Test list_tasks tool with mocked HTTP"""
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

    @pytest.mark.asyncio
    async def test_create_task_mock(self):
        """Test create_task tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "title": "New Task"}
            mock_post.return_value = mock_response

            result = await agent.create_task(
                title="New Task", project_id=1, description="Description"
            )

            assert "id" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_update_task_mock(self):
        """Test update_task tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "put", new_callable=AsyncMock) as mock_put:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "status": "done"}
            mock_put.return_value = mock_response

            result = await agent.update_task(task_id=1, status="done")

            assert result["status"] == "done"

        await agent.close()

    @pytest.mark.asyncio
    async def test_get_overdue_tasks_mock(self):
        """Test get_overdue_tasks tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = []
            mock_get.return_value = mock_response

            result = await agent.get_overdue_tasks(project_id=1)

            assert isinstance(result, list)

        await agent.close()

    @pytest.mark.asyncio
    async def test_get_project_stats_mock(self):
        """Test get_project_stats tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "get", new_callable=AsyncMock) as mock_get:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"todo": 5, "in-progress": 3, "done": 2}
            mock_get.return_value = mock_response

            result = await agent.get_project_stats(project_id=1)

            assert "todo" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_register_organization_mock(self):
        """Test register_organization tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"organization_id": 1, "user_id": 1}
            mock_post.return_value = mock_response

            result = await agent.register_organization(
                org_name="Test Org",
                email="admin@test.com",
                password="password123",
                full_name="Admin User",
            )

            assert "organization_id" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_create_project_mock(self):
        """Test create_project tool with mocked HTTP"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()
        agent.auth_token = "test_token"

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_response = MagicMock()
            mock_response.status_code = 200
            mock_response.json.return_value = {"id": 1, "name": "New Project"}
            mock_post.return_value = mock_response

            result = await agent.create_project(
                name="New Project", description="Description"
            )

            assert "id" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_process_user_request_respond(self):
        """Test process_user_request with respond action"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        # Mock the Gemini model
        with patch.object(agent.model, "generate_content") as mock_generate:
            mock_response = MagicMock()
            mock_response.text = '{"thought": "User asked for help", "action": "respond", "action_input": {"message": "I can help you!"}}'
            mock_generate.return_value = mock_response

            result = await agent.process_user_request("help")

            assert "I can help you!" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_agent_close(self):
        """Test agent close method"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        # Should not raise
        await agent.close()


class TestAgentExceptionHandling:
    """Test agent exception handling"""

    @pytest.mark.asyncio
    async def test_login_exception_handling(self):
        """Test login handles exceptions"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        with patch.object(agent.client, "post", new_callable=AsyncMock) as mock_post:
            mock_post.side_effect = Exception("Network error")

            result = await agent.login("test@example.com", "password")

            assert result["success"] is False
            assert "error" in result

        await agent.close()

    @pytest.mark.asyncio
    async def test_list_tasks_exception_handling(self):
        """Test list_tasks handles exceptions"""
        from app.agent.agent import TaskAgent

        agent = TaskAgent()

        with patch.object(agent.client, "get", new_callable=AsyncMock) as mock_get:
            mock_get.side_effect = Exception("Connection failed")

            result = await agent.list_tasks()

            assert "error" in result

        await agent.close()
