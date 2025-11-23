import asyncio
from collections.abc import Callable, Iterator
from contextlib import AbstractContextManager, contextmanager
from datetime import date
from functools import wraps
from typing import (
    Any,
    Literal,
    TypeVar,
    overload,
)
from uuid import UUID

from .async_client import AsyncClient
from .models import AgentConfig, ProgressEntry, ResponseObject, ResponseListResponse
from .types import ApiKeyMode, ApiProvider, Scope

T = TypeVar("T")


def sync_stream_wrapper(async_gen_func: Callable[..., Any]) -> Callable[..., Iterator[ProgressEntry]]:
    """Wrapper for async generator functions to make them sync iterators."""
    @wraps(async_gen_func)
    def wrapper(*args, **kwargs) -> Iterator[ProgressEntry]:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Same helpful error message as sync_wrapper
            import inspect
            import sys

            frame = inspect.currentframe()
            calling_frame = frame.f_back.f_back if frame and frame.f_back else None

            if calling_frame:
                func_name = calling_frame.f_code.co_name
                args = calling_frame.f_locals.get('args', ())
                kwargs = calling_frame.f_locals.get('kwargs', {})

                method_call = f"client.{func_name}("

                if args and len(args) > 1:
                    method_call += ", ".join(repr(arg) for arg in args[1:])

                if kwargs:
                    if len(args) > 1:
                        method_call += ", "
                    method_call += ", ".join(f"{k}={v!r}" for k, v in kwargs.items())

                method_call += ")"
            else:
                method_call = "client.invoke(..., stream=True)"

            error_msg = (
                "Cannot use synchronous Client with streaming in an async environment.\n\n"
            )

            if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                error_msg += (
                    "📓 For Jupyter/Colab notebooks, use AsyncClient instead:\n\n"
                    "    client = lumnisai.AsyncClient()\n"
                    "    async for update in client.invoke(..., stream=True):\n"
                    "        print(update.status)\n"
                )
            else:
                error_msg += (
                    "Use AsyncClient for streaming:\n\n"
                    "    async with lumnisai.AsyncClient() as client:\n"
                    "        async for update in client.invoke(..., stream=True):\n"
                    "            print(update.status)\n"
                )

            raise RuntimeError(error_msg)

        # Run the async generator in the sync context
        async_gen = async_gen_func(*args, **kwargs)

        # Convert async generator to sync iterator
        async def _collect_all():
            results = []
            async for item in await async_gen:
                results.append(item)
            return results

        # Get all results and return them as a sync iterator
        all_results = loop.run_until_complete(_collect_all())
        return iter(all_results)

    return wrapper


def sync_wrapper(async_func: Callable[..., T]) -> Callable[..., T]:
    @wraps(async_func)
    def wrapper(*args, **kwargs) -> T:
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)

        if loop.is_running():
            # Provide specific guidance for different environments
            import inspect
            import sys

            # Get the actual function name and arguments that were called
            frame = inspect.currentframe()
            calling_frame = frame.f_back.f_back if frame and frame.f_back else None

            if calling_frame:
                func_name = calling_frame.f_code.co_name
                # Get the arguments passed to the function
                args = calling_frame.f_locals.get('args', ())
                kwargs = calling_frame.f_locals.get('kwargs', {})

                # Construct the method call
                method_call = f"client.{func_name}("

                # Add positional args
                if args and len(args) > 1:  # Skip 'self'
                    method_call += ", ".join(repr(arg) for arg in args[1:])

                # Add keyword args
                if kwargs:
                    if len(args) > 1:
                        method_call += ", "
                    method_call += ", ".join(f"{k}={v!r}" for k, v in kwargs.items())

                method_call += ")"
            else:
                method_call = "client.invoke(...)"

            error_msg = (
                "Cannot use synchronous Client in an async environment.\n\n"
            )

            # Detect Jupyter/IPython
            if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                error_msg += (
                    "📓 For Jupyter/Colab notebooks, replace this:\n\n"
                    f"    client = lumnisai.Client()\n"
                    f"    response = {method_call}\n\n"
                    "With this:\n\n"
                    f"    client = lumnisai.AsyncClient()\n"
                    f"    response = await {method_call.replace('client.', 'client.')}\n"
                )
            else:
                error_msg += (
                    "Replace this:\n\n"
                    f"    client = lumnisai.Client()\n"
                    f"    response = {method_call}\n\n"
                    "With this:\n\n"
                    f"    async with lumnisai.AsyncClient() as client:\n"
                    f"        response = await {method_call.replace('client.', 'client.')}\n"
                )

            raise RuntimeError(error_msg)

        return loop.run_until_complete(async_func(*args, **kwargs))

    return wrapper


class SyncResourceProxy:
    def __init__(self, async_resource):
        self._async_resource = async_resource

    def __getattr__(self, name):
        attr = getattr(self._async_resource, name)
        if asyncio.iscoroutinefunction(attr):
            return sync_wrapper(attr)
        return attr


class Client:
    def __init__(
        self,
        *,
        api_key: str | None = None,
        base_url: str | None = None,
        tenant_id: str | None = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        scope: Scope = Scope.TENANT,
        _scoped_user_id: str | None = None,
    ):
        self._async_client = AsyncClient(
            api_key=api_key,
            base_url=base_url,
            tenant_id=tenant_id,
            timeout=timeout,
            max_retries=max_retries,
            scope=scope,
            _scoped_user_id=_scoped_user_id,
        )
        self._ensure_transport = sync_wrapper(self._async_client._ensure_transport)
        self._ensure_transport()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def close(self):
        sync_wrapper(self._async_client.close)()

    @property
    def responses(self):
        return SyncResourceProxy(self._async_client.responses)

    @property
    def threads(self):
        return SyncResourceProxy(self._async_client.threads)

    @property
    def external_api_keys(self):
        return SyncResourceProxy(self._async_client.external_api_keys)

    @property
    def api_keys(self):
        """Alias for external_api_keys for easier access."""
        return self.external_api_keys

    @property
    def tenant(self):
        return SyncResourceProxy(self._async_client.tenant)

    @property
    def users(self):
        return SyncResourceProxy(self._async_client.users)

    @property
    def integrations(self):
        return SyncResourceProxy(self._async_client.integrations)

    @property
    def model_preferences(self):
        return SyncResourceProxy(self._async_client.model_preferences)

    @property
    def mcp_servers(self):
        return SyncResourceProxy(self._async_client.mcp_servers)

    @property
    def files(self):
        """
        Access file management operations.
        
        Provides methods for uploading, searching, retrieving, and managing files
        with semantic search capabilities.
        """
        return SyncResourceProxy(self._async_client.files)

    @property
    def skills(self):
        """
        Access skills management operations.
        
        Provides methods for creating, listing, retrieving, updating, and deleting
        skill guidelines.
        """
        return SyncResourceProxy(self._async_client.skills)

    def for_user(self, user_id: str) -> "Client":
        return Client(
            api_key=self._async_client._config.api_key,
            base_url=self._async_client._config.base_url,
            tenant_id=str(self._async_client._config.tenant_id),
            timeout=self._async_client._config.timeout,
            max_retries=self._async_client._config.max_retries,
            scope=self._async_client._default_scope,
            _scoped_user_id=user_id,
        )

    @contextmanager
    def as_user(self, user_id: str) -> AbstractContextManager["Client"]:
        client = self.for_user(user_id)
        try:
            yield client
        finally:
            client.close()

    @overload
    def invoke(
        self,
        messages: str | dict[str, str] | list[dict[str, str]] | None = None,
        *,
        task: str | dict[str, str] | list[dict[str, str]] | None = None,
        prompt: str | None = None,
        stream: Literal[False] = False,
        show_progress: bool = True,
        user_id: str | UUID | None = None,
        scope: Scope | None = None,
        thread_id: str | None = None,
        idempotency_key: str | None = None,
        poll_interval: float = 2.0,
        agent_config: AgentConfig | dict | None = None,
        **options,
    ) -> ResponseObject: ...

    @overload
    def invoke(
        self,
        messages: str | dict[str, str] | list[dict[str, str]] | None = None,
        *,
        task: str | dict[str, str] | list[dict[str, str]] | None = None,
        prompt: str | None = None,
        stream: Literal[True],
        show_progress: bool = False,
        user_id: str | UUID | None = None,
        scope: Scope | None = None,
        thread_id: str | None = None,
        idempotency_key: str | None = None,
        poll_interval: float = 2.0,
        agent_config: AgentConfig | dict | None = None,
        **options,
    ) -> Iterator[ProgressEntry]: ...

    def invoke(
        self,
        messages: str | dict[str, str] | list[dict[str, str]] | None = None,
        *,
        task: str | dict[str, str] | list[dict[str, str]] | None = None,
        prompt: str | None = None,
        stream: bool = False,
        show_progress: bool = True,
        user_id: str | UUID | None = None,
        scope: Scope | None = None,
        thread_id: str | None = None,
        idempotency_key: str | None = None,
        poll_interval: float = 2.0,
        agent_config: AgentConfig | dict | None = None,
        **options,
    ) -> ResponseObject | Iterator[ProgressEntry]:
        if stream:
            # For streaming, we need a special approach since sync streaming is complex
            # We'll collect all responses and return them as an iterator
            invoke_stream_wrapped = sync_stream_wrapper(self._async_client.invoke)
            return invoke_stream_wrapped(
                messages,
                task=task,
                prompt=prompt,
                stream=True,
                show_progress=show_progress,
                user_id=user_id,
                scope=scope,
                thread_id=thread_id,
                idempotency_key=idempotency_key,
                poll_interval=poll_interval,
                agent_config=agent_config,
                **options,
            )
        else:
            # Regular blocking invoke
            invoke_wrapped = sync_wrapper(self._async_client.invoke)
            return invoke_wrapped(
                messages,
                task=task,
                prompt=prompt,
                stream=False,
                show_progress=show_progress,
                user_id=user_id,
                scope=scope,
                thread_id=thread_id,
                idempotency_key=idempotency_key,
                poll_interval=poll_interval,
                agent_config=agent_config,
                **options,
            )


    # Direct resource access methods for flattened API
    def get_response(self, response_id: str, *, wait: float | None = None) -> ResponseObject:
        get_response_async = sync_wrapper(self._async_client.get_response)
        return get_response_async(response_id, wait=wait)

    def list_responses(
        self,
        *,
        user_id: str | UUID | None = None,
        status: Literal["queued", "in_progress", "succeeded", "failed", "cancelled"] | None = None,
        start_date: date | None = None,
        end_date: date | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> ResponseListResponse:
        """List responses with optional filtering."""
        list_responses_async = sync_wrapper(self._async_client.list_responses)
        return list_responses_async(
            user_id=user_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset,
        )

    def cancel_response(self, response_id: str) -> ResponseObject:
        cancel_response_async = sync_wrapper(self._async_client.cancel_response)
        return cancel_response_async(response_id)

    def list_threads(self, *, user_id: str | None = None, limit: int = 50, cursor: str | None = None):
        list_threads_async = sync_wrapper(self._async_client.list_threads)
        return list_threads_async(user_id=user_id, limit=limit, cursor=cursor)

    def get_thread(self, thread_id: str):
        get_thread_async = sync_wrapper(self._async_client.get_thread)
        return get_thread_async(thread_id)

    def create_thread(self, *, user_id: str | None = None, title: str | None = None):
        create_thread_async = sync_wrapper(self._async_client.create_thread)
        return create_thread_async(user_id=user_id, title=title)

    def delete_thread(self, thread_id: str):
        delete_thread_async = sync_wrapper(self._async_client.delete_thread)
        return delete_thread_async(thread_id)

    # User management flattened methods
    def create_user(self, *, email: str, first_name: str | None = None, last_name: str | None = None):
        create_user_async = sync_wrapper(self._async_client.create_user)
        return create_user_async(email=email, first_name=first_name, last_name=last_name)

    def get_user(self, user_identifier: str | UUID):
        get_user_async = sync_wrapper(self._async_client.get_user)
        return get_user_async(user_identifier)

    def update_user(self, user_identifier: str | UUID, *, first_name: str | None = None, last_name: str | None = None):
        update_user_async = sync_wrapper(self._async_client.update_user)
        return update_user_async(user_identifier, first_name=first_name, last_name=last_name)

    def delete_user(self, user_identifier: str | UUID):
        delete_user_async = sync_wrapper(self._async_client.delete_user)
        return delete_user_async(user_identifier)

    def list_users(self, *, page: int = 1, page_size: int = 20):
        list_users_async = sync_wrapper(self._async_client.list_users)
        return list_users_async(page=page, page_size=page_size)

    # External API Key helpers
    def add_api_key(self, provider: str | ApiProvider, api_key: str):
        """Add an external API key for BYO keys mode."""
        add_api_key_async = sync_wrapper(self._async_client.add_api_key)
        return add_api_key_async(provider, api_key)

    def list_api_keys(self):
        """List all stored external API keys."""
        list_api_keys_async = sync_wrapper(self._async_client.list_api_keys)
        return list_api_keys_async()

    def get_api_key(self, key_id: str | UUID):
        """Get a specific external API key by ID."""
        get_api_key_async = sync_wrapper(self._async_client.get_api_key)
        return get_api_key_async(key_id)

    def delete_api_key(self, provider: str | ApiProvider):
        """Delete an external API key."""
        delete_api_key_async = sync_wrapper(self._async_client.delete_api_key)
        return delete_api_key_async(provider)

    def get_api_key_mode(self):
        """Get the current API key mode (platform or byo_keys)."""
        get_api_key_mode_async = sync_wrapper(self._async_client.get_api_key_mode)
        return get_api_key_mode_async()

    def set_api_key_mode(self, mode: str | ApiKeyMode):
        """Set the API key mode (platform or byo_keys)."""
        set_api_key_mode_async = sync_wrapper(self._async_client.set_api_key_mode)
        return set_api_key_mode_async(mode)

    # Integration wrapper methods
    def list_apps(self, *, include_available: bool = False):
        """List apps enabled for the tenant."""
        list_apps_async = sync_wrapper(self._async_client.list_apps)
        return list_apps_async(include_available=include_available)

    def is_app_enabled(self, app_name: str):
        """Check if a specific app is enabled for the tenant."""
        is_app_enabled_async = sync_wrapper(self._async_client.is_app_enabled)
        return is_app_enabled_async(app_name)

    def set_app_enabled(self, app_name: str, *, enabled: bool):
        """Enable or disable an app for the tenant."""
        set_app_enabled_async = sync_wrapper(self._async_client.set_app_enabled)
        return set_app_enabled_async(app_name, enabled=enabled)

    def initiate_connection(
        self,
        *,
        user_id: str,
        app_name: str,
        integration_id: str | None = None,
        redirect_url: str | None = None,
    ):
        """Initiate a connection to an external app."""
        initiate_connection_async = sync_wrapper(self._async_client.initiate_connection)
        return initiate_connection_async(
            user_id=user_id,
            app_name=app_name,
            integration_id=integration_id,
            redirect_url=redirect_url
        )

    def get_connection_status(self, user_id: str, app_name: str):
        """Get connection status for a specific app."""
        get_connection_status_async = sync_wrapper(self._async_client.get_connection_status)
        return get_connection_status_async(user_id, app_name)

    def wait_for_connection(
        self,
        user_id: str,
        app_name: str,
        *,
        timeout: float = 300.0,
        poll_interval: float = 5.0,
        target_status: str = "active"
    ):
        """Wait for a connection to reach a specific status.
        
        Args:
            user_id: The user ID
            app_name: The app name to check connection for
            timeout: Maximum time to wait in seconds (default: 300s/5min)
            poll_interval: Time between status checks in seconds (default: 10s)
            target_status: The status to wait for (default: "active")
            
        Returns:
            The final ConnectionStatus when target status is reached
            
        Raises:
            TimeoutError: If the connection doesn't reach target status within timeout
        """
        wait_for_connection_async = sync_wrapper(self._async_client.wait_for_connection)
        return wait_for_connection_async(
            user_id=user_id,
            app_name=app_name,
            timeout=timeout,
            poll_interval=poll_interval,
            target_status=target_status
        )

    def list_connections(self, user_id: str, *, app_filter: str | None = None):
        """List all connections for a user."""
        list_connections_async = sync_wrapper(self._async_client.list_connections)
        return list_connections_async(user_id, app_filter=app_filter)

    def get_integration_tools(self, user_id: str, *, app_filter: list[str] | None = None):
        """Get available tools based on user's active connections."""
        get_integration_tools_async = sync_wrapper(self._async_client.get_integration_tools)
        return get_integration_tools_async(user_id, app_filter=app_filter)

    # Model Preferences helper methods
    def get_model_preferences(self, *, include_defaults: bool = True):
        """Get model preferences for the tenant."""
        get_model_preferences_async = sync_wrapper(self._async_client.get_model_preferences)
        return get_model_preferences_async(include_defaults=include_defaults)

    def update_model_preferences(self, preferences):
        """Update multiple model preferences at once."""
        update_model_preferences_async = sync_wrapper(self._async_client.update_model_preferences)
        return update_model_preferences_async(preferences)

    # MCP Server Management convenience methods
    def create_mcp_server(self, *, name: str, transport: Literal["stdio", "streamable_http", "sse"], 
                         scope: Literal["tenant", "user"], **kwargs):
        """Create a new MCP server configuration."""
        create_mcp_server_async = sync_wrapper(self._async_client.create_mcp_server)
        return create_mcp_server_async(name=name, transport=transport, scope=scope, **kwargs)

    def get_mcp_server(self, server_id: str | UUID):
        """Get a specific MCP server by ID."""
        get_mcp_server_async = sync_wrapper(self._async_client.get_mcp_server)
        return get_mcp_server_async(server_id)

    def list_mcp_servers(self, *, scope: str | None = None, user_identifier: str | None = None,
                        is_active: bool | None = None, skip: int = 0, limit: int = 100):
        """List MCP servers with optional filtering."""
        list_mcp_servers_async = sync_wrapper(self._async_client.list_mcp_servers)
        return list_mcp_servers_async(scope=scope, user_identifier=user_identifier, 
                                    is_active=is_active, skip=skip, limit=limit)

    def update_mcp_server(self, server_id: str | UUID, **kwargs):
        """Update an MCP server configuration."""
        update_mcp_server_async = sync_wrapper(self._async_client.update_mcp_server)
        return update_mcp_server_async(server_id, **kwargs)

    def delete_mcp_server(self, server_id: str | UUID):
        """Delete an MCP server."""
        delete_mcp_server_async = sync_wrapper(self._async_client.delete_mcp_server)
        return delete_mcp_server_async(server_id)

    def list_mcp_server_tools(self, server_id: str | UUID):
        """List tools provided by an MCP server."""
        list_mcp_server_tools_async = sync_wrapper(self._async_client.list_mcp_server_tools)
        return list_mcp_server_tools_async(server_id)

    def test_mcp_server(self, server_id: str | UUID):
        """Test connection to an MCP server."""
        test_mcp_server_async = sync_wrapper(self._async_client.test_mcp_server)
        return test_mcp_server_async(server_id)

    # File management convenience methods
    def upload_file(self, *, file_path=None, file_content=None, file_name=None,
                   scope=None, user_id=None, tags=None, duplicate_handling=None):
        """Upload a file for processing and semantic search."""
        upload_file_async = sync_wrapper(self._async_client.upload_file)
        return upload_file_async(
            file_path=file_path,
            file_content=file_content,
            file_name=file_name,
            scope=scope,
            user_id=user_id,
            tags=tags,
            duplicate_handling=duplicate_handling
        )

    def download_file(self, file_id, *, user_id=None, save_path=None):
        """Download the original file."""
        download_file_async = sync_wrapper(self._async_client.download_file)
        return download_file_async(file_id, user_id=user_id, save_path=save_path)

    def delete_file(self, file_id, *, user_id=None, hard_delete=True):
        """Delete a file."""
        delete_file_async = sync_wrapper(self._async_client.delete_file)
        return delete_file_async(file_id, user_id=user_id, hard_delete=hard_delete)

    def search_files(self, query, *, user_id=None, limit=10, min_score=0.0,
                    file_types=None, tags=None):
        """Perform semantic search across files."""
        search_files_async = sync_wrapper(self._async_client.search_files)
        return search_files_async(
            query,
            user_id=user_id,
            limit=limit,
            min_score=min_score,
            file_types=file_types,
            tags=tags
        )

    def list_files(self, *, user_id=None, scope=None, file_type=None,
                  status=None, tags=None, page=1, limit=20):
        """List files with optional filters and pagination."""
        list_files_async = sync_wrapper(self._async_client.list_files)
        return list_files_async(
            user_id=user_id,
            scope=scope,
            file_type=file_type,
            status=status,
            tags=tags,
            page=page,
            limit=limit
        )

    def get_file(self, file_id, *, user_id=None):
        """Get file metadata by ID."""
        get_file_async = sync_wrapper(self._async_client.get_file)
        return get_file_async(file_id, user_id=user_id)

    def get_file_content(self, file_id, *, user_id=None, content_type=None,
                        start_line=None, end_line=None):
        """Get file content."""
        get_file_content_async = sync_wrapper(self._async_client.get_file_content)
        return get_file_content_async(
            file_id,
            user_id=user_id,
            content_type=content_type,
            start_line=start_line,
            end_line=end_line
        )

    def get_file_status(self, file_id, *, user_id=None):
        """Get the processing status of a file."""
        get_file_status_async = sync_wrapper(self._async_client.get_file_status)
        return get_file_status_async(file_id, user_id=user_id)

    # Skills management convenience methods
    def create_skill(
        self,
        *,
        name: str,
        description: str,
        content: str,
        category: str | None = None,
        version: str = "1.0.0",
        user_id: str | UUID | None = None,
    ):
        """Create a new skill guideline."""
        create_skill_async = sync_wrapper(self._async_client.create_skill)
        return create_skill_async(
            name=name,
            description=description,
            content=content,
            category=category,
            version=version,
            user_id=user_id,
        )

    def list_skills(
        self,
        *,
        category: str | None = None,
        is_active: bool | None = True,
        page: int = 1,
        page_size: int = 50,
    ):
        """List skill guidelines with optional filtering."""
        list_skills_async = sync_wrapper(self._async_client.list_skills)
        return list_skills_async(
            category=category,
            is_active=is_active,
            page=page,
            page_size=page_size,
        )

    def get_skill(self, skill_id: str | UUID):
        """Get a skill guideline by ID."""
        get_skill_async = sync_wrapper(self._async_client.get_skill)
        return get_skill_async(skill_id)

    def update_skill(
        self,
        skill_id: str | UUID,
        *,
        name: str | None = None,
        description: str | None = None,
        content: str | None = None,
        category: str | None = None,
        version: str | None = None,
        is_active: bool | None = None,
    ):
        """Update a skill guideline."""
        update_skill_async = sync_wrapper(self._async_client.update_skill)
        return update_skill_async(
            skill_id,
            name=name,
            description=description,
            content=content,
            category=category,
            version=version,
            is_active=is_active,
        )

    def delete_skill(self, skill_id: str | UUID):
        """Delete a skill guideline."""
        delete_skill_async = sync_wrapper(self._async_client.delete_skill)
        return delete_skill_async(skill_id)




