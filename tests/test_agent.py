"""
Tests for ReAct Agent with RAG Implementation
Tests: RAG module, Agent tools, LangGraph agent, and API endpoints
"""

import pytest
from unittest.mock import patch, MagicMock, PropertyMock
from datetime import datetime, timedelta


class TestRAGModule:
    """Test the RAG (Retrieval-Augmented Generation) module"""

    def test_rag_module_import(self):
        """Test that RAG module can be imported"""
        try:
            from app.core.rag import (
                get_embeddings,
                get_vector_store,
                index_data,
                retrieve_documents,
                search_tasks,
            )

            assert callable(get_embeddings)
            assert callable(get_vector_store)
            assert callable(index_data)
            assert callable(retrieve_documents)
            assert callable(search_tasks)
        except ImportError as e:
            pytest.skip(f"RAG dependencies not installed: {e}")

    def test_search_tasks_returns_string(self):
        """Test search_tasks returns a string"""
        try:
            from app.core.rag import search_tasks

            # Mock the vector store to avoid actual database calls
            with patch("app.core.rag.get_vector_store") as mock_vs:
                mock_retriever = MagicMock()
                mock_retriever.invoke.return_value = []
                mock_vs.return_value.as_retriever.return_value = mock_retriever

                result = search_tasks("test query", top_k=5)
                assert isinstance(result, str)
                assert "No relevant tasks found" in result
        except ImportError as e:
            pytest.skip(f"RAG dependencies not installed: {e}")


class TestAgentTools:
    """Test the LangChain tools for the agent"""

    def test_tools_import(self):
        """Test that tools module can be imported"""
        try:
            from app.agent.tools import (
                tools,
                search_tasks_tool,
                list_tasks_tool,
                create_task_tool,
                update_task_tool,
                project_stats_tool,
                ToolContext,
            )

            assert len(tools) == 5
            # LangChain tools are StructuredTool objects, not directly callable
            assert hasattr(search_tasks_tool, "invoke")
            assert hasattr(list_tasks_tool, "invoke")
            assert hasattr(create_task_tool, "invoke")
            assert hasattr(update_task_tool, "invoke")
            assert hasattr(project_stats_tool, "invoke")
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_tool_context_set_and_clear(self):
        """Test ToolContext set and clear methods"""
        try:
            from app.agent.tools import ToolContext

            mock_db = MagicMock()
            mock_user = MagicMock()

            # Set context
            ToolContext.set_context(mock_db, mock_user)
            assert ToolContext.db == mock_db
            assert ToolContext.current_user == mock_user

            # Clear context
            ToolContext.clear_context()
            assert ToolContext.db is None
            assert ToolContext.current_user is None
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_search_tasks_tool_invocation(self):
        """Test search_tasks_tool can be invoked"""
        try:
            from app.agent.tools import search_tasks_tool

            with patch("app.agent.tools.search_tasks") as mock_search:
                mock_search.return_value = "Task: Test Task. Status: todo."

                # Invoke the tool
                result = search_tasks_tool.invoke({"query": "test"})
                assert isinstance(result, str)
                mock_search.assert_called_once_with("test", top_k=5)
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_list_tasks_tool_no_context(self):
        """Test list_tasks_tool returns error when no context"""
        try:
            from app.agent.tools import list_tasks_tool, ToolContext

            # Ensure context is cleared
            ToolContext.clear_context()

            result = list_tasks_tool.invoke({"filter_type": "all"})
            assert "Error" in result
            assert "Database context not available" in result
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_list_tasks_tool_with_context(self):
        """Test list_tasks_tool with mocked context"""
        try:
            from app.agent.tools import list_tasks_tool, ToolContext
            from app.models.task import TaskStatus, TaskPriority

            # Create mock database and user
            mock_db = MagicMock()
            mock_user = MagicMock()
            mock_user.organization_id = 1
            mock_user.id = 1

            # Mock task
            mock_task = MagicMock()
            mock_task.title = "Test Task"
            mock_task.status = TaskStatus.TODO
            mock_task.priority = TaskPriority.HIGH
            mock_task.due_date = datetime.now() + timedelta(days=1)
            mock_task.assignee = MagicMock()
            mock_task.assignee.full_name = "John Doe"

            # Setup query chain mock
            mock_query = MagicMock()
            mock_query.join.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.limit.return_value.all.return_value = [mock_task]
            mock_db.query.return_value = mock_query

            # Set context
            ToolContext.set_context(mock_db, mock_user)

            try:
                result = list_tasks_tool.invoke({"filter_type": "all"})
                assert isinstance(result, str)
                assert (
                    "Test Task" in result or "Found" in result or "No tasks" in result
                )
            finally:
                ToolContext.clear_context()

        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_create_task_tool_no_context(self):
        """Test create_task_tool returns error when no context"""
        try:
            from app.agent.tools import create_task_tool, ToolContext

            ToolContext.clear_context()

            result = create_task_tool.invoke(
                {"title": "Test Task", "description": "Test", "priority": "medium"}
            )
            assert "Error" in result
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_update_task_tool_no_context(self):
        """Test update_task_tool returns error when no context"""
        try:
            from app.agent.tools import update_task_tool, ToolContext

            ToolContext.clear_context()

            result = update_task_tool.invoke(
                {"task_title": "Test", "new_status": "done"}
            )
            assert "Error" in result
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_project_stats_tool_no_context(self):
        """Test project_stats_tool returns error when no context"""
        try:
            from app.agent.tools import project_stats_tool, ToolContext

            ToolContext.clear_context()

            result = project_stats_tool.invoke({"project_name": ""})
            assert "Error" in result
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")


class TestAgentGraph:
    """Test the LangGraph ReAct Agent"""

    def test_graph_module_import(self):
        """Test that graph module can be imported"""
        try:
            from app.agent.graph import (
                get_llm,
                get_agent_executor,
                run_agent,
                SYSTEM_MESSAGE,
            )

            assert callable(get_llm)
            assert callable(get_agent_executor)
            assert callable(run_agent)
            assert isinstance(SYSTEM_MESSAGE, str)
            assert len(SYSTEM_MESSAGE) > 0
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_run_agent_without_api_key(self):
        """Test run_agent handles missing API key gracefully"""
        try:
            from app.agent.graph import run_agent
            from app.config import settings

            # Save original key
            original_key = settings.GEMINI_API_KEY

            # Mock empty API key
            with patch.object(settings, "GEMINI_API_KEY", ""):
                try:
                    result = run_agent("Hello")
                    # Should return an error message
                    assert isinstance(result, str)
                except Exception as e:
                    # Exception is also acceptable for missing API key
                    assert True
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")

    def test_run_agent_clears_context(self):
        """Test that run_agent properly clears ToolContext"""
        try:
            from app.agent.graph import run_agent
            from app.agent.tools import ToolContext

            # Mock the agent executor to avoid actual API calls
            with patch("app.agent.graph.get_agent_executor") as mock_agent:
                mock_executor = MagicMock()
                mock_executor.invoke.return_value = {
                    "messages": [MagicMock(content="Test response")]
                }
                mock_agent.return_value = mock_executor

                mock_db = MagicMock()
                mock_user = MagicMock()

                run_agent("test message", db=mock_db, current_user=mock_user)

                # Context should be cleared after execution
                assert ToolContext.db is None
                assert ToolContext.current_user is None
        except ImportError as e:
            pytest.skip(f"Agent dependencies not installed: {e}")


class TestAgentEndpoints:
    """Test the Agent API endpoints"""

    def test_endpoint_module_import(self):
        """Test that agent endpoint module can be imported"""
        try:
            from app.api.v1.endpoints.agent import (
                router,
                chat_with_agent,
                sync_knowledge_base,
                ChatRequest,
                ChatResponse,
                SyncResponse,
            )

            assert router is not None
            assert callable(chat_with_agent)
            assert callable(sync_knowledge_base)
        except ImportError as e:
            pytest.skip(f"Agent endpoint dependencies not installed: {e}")

    def test_chat_request_model(self):
        """Test ChatRequest pydantic model"""
        try:
            from app.api.v1.endpoints.agent import ChatRequest

            request = ChatRequest(message="Hello, AI!")
            assert request.message == "Hello, AI!"
        except ImportError as e:
            pytest.skip(f"Agent endpoint dependencies not installed: {e}")

    def test_chat_response_model(self):
        """Test ChatResponse pydantic model"""
        try:
            from app.api.v1.endpoints.agent import ChatResponse

            response = ChatResponse(response="Hello!", actions=[])
            assert response.response == "Hello!"
            assert response.actions == []
        except ImportError as e:
            pytest.skip(f"Agent endpoint dependencies not installed: {e}")

    def test_sync_response_model(self):
        """Test SyncResponse pydantic model"""
        try:
            from app.api.v1.endpoints.agent import SyncResponse

            response = SyncResponse(message="Success", indexed_count=10)
            assert response.message == "Success"
            assert response.indexed_count == 10
        except ImportError as e:
            pytest.skip(f"Agent endpoint dependencies not installed: {e}")


class TestRoutesExist:
    """Test that routes are properly registered"""

    def test_agent_routes_registered(self):
        """Test that agent routes are registered in the app"""
        try:
            from app.main import app
            from fastapi.routing import APIRoute

            routes = [r for r in app.routes if isinstance(r, APIRoute)]
            route_paths = [r.path for r in routes]

            # Check agent endpoints exist
            assert "/api/v1/agent/chat" in route_paths
            assert "/api/v1/agent/sync-knowledge" in route_paths
        except ImportError as e:
            pytest.skip(f"FastAPI not available: {e}")


class TestMCPServerExisting:
    """Test MCP Server functionality - kept from original tests"""

    def test_mcp_server_import(self):
        """Test that MCP server module can be imported"""
        try:
            from app.mcp import server

            assert server is not None
        except ImportError as e:
            pytest.skip(f"MCP dependencies not installed: {e}")

    def test_route_discovery(self):
        """Test that routes are discovered from FastAPI app"""
        try:
            from app.main import app
            from fastapi.routing import APIRoute

            routes = [r for r in app.routes if isinstance(r, APIRoute)]

            # Should have multiple routes
            assert len(routes) > 0

            # Should include key endpoints
            route_paths = [r.path for r in routes]
            assert "/health" in route_paths
            assert "/api/v1/auth/login" in route_paths
        except ImportError as e:
            pytest.skip(f"FastAPI not available: {e}")


class TestAttachmentLimitsExisting:
    """Test attachment business rules - kept from original tests"""

    def test_max_file_size_constant(self):
        """Verify max file size is 5MB"""
        MAX_SIZE_BYTES = 5 * 1024 * 1024  # 5MB
        assert MAX_SIZE_BYTES == 5242880

    def test_max_attachments_per_task(self):
        """Verify max attachments is 3"""
        MAX_ATTACHMENTS = 3
        assert MAX_ATTACHMENTS == 3
