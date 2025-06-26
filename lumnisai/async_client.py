
import asyncio
import inspect
import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncContextManager, AsyncGenerator, Callable, Dict, List, Literal, Optional, Union, overload
from uuid import UUID

from ._transport import HTTPTransport
from .config import Config
from .constants import DEFAULT_POLL_INTERVAL, LONG_POLL_TIMEOUT
from .exceptions import MissingUserId, NotImplementedYetError, TenantScopeUserIdConflict
from .models import ResponseObject, ProgressEntry
from .resources import (
    ExternalApiKeysResource,
    ResponsesResource,
    TenantResource,
    ThreadsResource,
    UsersResource,
)
from .types import ApiKeyMode, ApiProvider, Scope

logger = logging.getLogger("lumnisai")


class AsyncClient:

    def __init__(
        self,
        *,
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        timeout: float = 30.0,
        scope: Scope = Scope.USER,
        max_retries: int = 3,
        _scoped_user_id: Optional[str] = None,
    ):
        self._config = Config(
            api_key=api_key,
            base_url=base_url,
            tenant_id=tenant_id,
            timeout=timeout,
            max_retries=max_retries,
        )
        self._scoped_user_id = _scoped_user_id
        self._default_scope = scope
        self._transport: Optional[HTTPTransport] = None
        self._initialized = False

        tenant_log = str(self._config.tenant_id) if self._config.tenant_id else "from API key context"
        logger.info(
            f"LumnisAI AsyncClient initialized for tenant {tenant_log}",
            extra={"tenant_id": tenant_log},
        )

    async def __aenter__(self):
        if not self._initialized:
            await self._ensure_transport()
            self._initialized = True
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()

    async def close(self):
        if self._transport:
            await self._transport.close()
            self._transport = None
        self._initialized = False

    async def _ensure_transport(self):
        if not self._transport:
            self._transport = HTTPTransport(
                base_url=self._config.base_url,
                api_key=self._config.api_key,
                timeout=self._config.timeout,
                max_retries=self._config.max_retries,
            )
            self._initialized = True

    async def init(self) -> None:
        await self._ensure_transport()
        self._initialized = True

    @property
    def responses(self) -> ResponsesResource:
        if not self._transport:
            raise RuntimeError(
                "AsyncClient not initialized. Use 'async with client:' context manager "
                "or call 'await client.init()' before accessing resources directly. "
                "For direct API calls, use 'await client.invoke()' which auto-initializes."
            )
        return ResponsesResource(self._transport, tenant_id=self._config.tenant_id)

    @property
    def threads(self) -> ThreadsResource:
        if not self._transport:
            raise RuntimeError(
                "AsyncClient not initialized. Use 'async with client:' context manager "
                "or call 'await client.init()' before accessing resources directly. "
                "For direct API calls, use 'await client.invoke()' which auto-initializes."
            )
        return ThreadsResource(self._transport, tenant_id=self._config.tenant_id)

    @property
    def external_api_keys(self) -> ExternalApiKeysResource:
        if not self._transport:
            raise RuntimeError(
                "AsyncClient not initialized. Use 'async with client:' context manager "
                "or call 'await client.init()' before accessing resources directly. "
                "For direct API calls, use 'await client.invoke()' which auto-initializes."
            )
        return ExternalApiKeysResource(self._transport, tenant_id=self._config.tenant_id)

    @property
    def tenant(self) -> TenantResource:
        if not self._transport:
            raise RuntimeError(
                "AsyncClient not initialized. Use 'async with client:' context manager "
                "or call 'await client.init()' before accessing resources directly. "
                "For direct API calls, use 'await client.invoke()' which auto-initializes."
            )
        return TenantResource(self._transport, tenant_id=self._config.tenant_id)

    @property
    def users(self) -> UsersResource:
        if not self._transport:
            raise RuntimeError(
                "AsyncClient not initialized. Use 'async with client:' context manager "
                "or call 'await client.init()' before accessing resources directly. "
                "For direct API calls, use 'await client.invoke()' which auto-initializes."
            )
        return UsersResource(self._transport, tenant_id=self._config.tenant_id)

    def for_user(self, user_id: str) -> "AsyncClient":
        return AsyncClient(
            api_key=self._config.api_key,
            base_url=self._config.base_url,
            tenant_id=str(self._config.tenant_id) if self._config.tenant_id else None,
            timeout=self._config.timeout,
            scope=Scope.USER,
            max_retries=self._config.max_retries,
            _scoped_user_id=user_id,
        )

    @asynccontextmanager
    async def as_user(self, user_id: str) -> AsyncContextManager["AsyncClient"]:
        client = self.for_user(user_id)
        async with client:
            yield client

    @overload
    async def invoke(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        *,
        task: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        prompt: str = None,
        stream: Literal[False] = False,
        show_progress: bool = False,
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> ResponseObject: ...

    @overload
    async def invoke(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        *,
        task: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        prompt: str = None,
        stream: Literal[True],
        show_progress: bool = False,
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> AsyncGenerator[ProgressEntry, None]: ...

    async def invoke(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        *,
        task: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        prompt: str = None,
        stream: bool = False,
        show_progress: bool = False,
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> Union[ResponseObject, AsyncGenerator[ProgressEntry, None]]:
        # Handle parameter compatibility and validation
        resolved_input = self._resolve_input_parameters(messages, task, prompt)
        
        # Auto-initialize on first use
        await self._ensure_transport()
        
        if stream:
            # Return async generator for streaming
            return self._create_stream_generator(
                input_data=resolved_input,
                user_id=user_id,
                scope=scope or self._default_scope,
                thread_id=thread_id,
                idempotency_key=idempotency_key,
                poll_interval=poll_interval,
                wait_timeout=wait_timeout,
                **options
            )
        else:
            # Return single response (blocking)
            progress_callback = self._create_simple_progress_callback() if show_progress else None
            return await self._invoke_async(
                input_data=resolved_input,
                user_id=user_id,
                scope=scope or self._default_scope,
                thread_id=thread_id,
                idempotency_key=idempotency_key,
                wait=True,
                progress_callback=progress_callback,
                poll_interval=poll_interval,
                wait_timeout=wait_timeout,
                **options
            )


    async def invoke_stream(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        *,
        task: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        prompt: str = None,
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> AsyncGenerator[ResponseObject, None]:
        """
        Deprecated: Use invoke(stream=True) instead.
        This method is kept for backwards compatibility.
        """
        import warnings
        warnings.warn(
            "invoke_stream() is deprecated. Use invoke(stream=True) instead.",
            DeprecationWarning,
            stacklevel=2
        )
        
        # Handle parameter compatibility
        resolved_input = self._resolve_input_parameters(messages, task, prompt)
        
        # Delegate to the new invoke method with stream=True
        async for update in await self.invoke(
            messages=resolved_input,
            stream=True,
            user_id=user_id,
            scope=scope,
            thread_id=thread_id,
            idempotency_key=idempotency_key,
            poll_interval=poll_interval,
            wait_timeout=wait_timeout,
            **options
        ):
            yield update

    # Direct resource access methods for flattened API
    async def get_response(self, response_id: str, *, wait: Optional[float] = None) -> ResponseObject:
        await self._ensure_transport()
        return await self.responses.get(response_id, wait=wait)

    async def list_responses(self, *, user_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None):
        await self._ensure_transport()
        return await self.responses.list(user_id=user_id, limit=limit, cursor=cursor)

    async def cancel_response(self, response_id: str) -> ResponseObject:
        await self._ensure_transport()
        return await self.responses.cancel(response_id)

    async def list_threads(self, *, user_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None):
        await self._ensure_transport()
        return await self.threads.list(user_id=user_id, limit=limit, cursor=cursor)

    async def get_thread(self, thread_id: str):
        await self._ensure_transport()
        return await self.threads.get(thread_id)

    async def create_thread(self, *, user_id: Optional[str] = None, title: Optional[str] = None):
        await self._ensure_transport()
        return await self.threads.create(user_id=user_id, title=title)

    async def delete_thread(self, thread_id: str):
        await self._ensure_transport()
        return await self.threads.delete(thread_id)
    
    # User management flattened methods
    async def create_user(self, *, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
        await self._ensure_transport()
        return await self.users.create(email=email, first_name=first_name, last_name=last_name)
    
    async def get_user(self, user_identifier: Union[str, UUID]):
        await self._ensure_transport()
        return await self.users.get(user_identifier)
    
    async def update_user(self, user_identifier: Union[str, UUID], *, first_name: Optional[str] = None, last_name: Optional[str] = None):
        await self._ensure_transport()
        return await self.users.update(user_identifier, first_name=first_name, last_name=last_name)
    
    async def delete_user(self, user_identifier: Union[str, UUID]):
        await self._ensure_transport()
        return await self.users.delete(user_identifier)
    
    async def list_users(self, *, page: int = 1, page_size: int = 20):
        await self._ensure_transport()
        return await self.users.list(page=page, page_size=page_size)
    
    # External API Key helpers
    async def add_api_key(
        self,
        provider: Union[str, ApiProvider],
        api_key: str,
    ):
        """Add an external API key for BYO keys mode."""
        await self._ensure_transport()
        return await self.external_api_keys.store(
            provider=provider,
            api_key=api_key,
        )
    
    async def list_api_keys(self):
        """List all stored external API keys."""
        await self._ensure_transport()
        return await self.external_api_keys.list()
    
    async def get_api_key(self, key_id: Union[str, UUID]):
        """Get a specific external API key by ID."""
        await self._ensure_transport()
        return await self.external_api_keys.get(key_id)
    
    async def delete_api_key(
        self,
        provider: Union[str, ApiProvider],
    ):
        """Delete an external API key."""
        await self._ensure_transport()
        return await self.external_api_keys.delete(provider)
    
    async def get_api_key_mode(self):
        """Get the current API key mode (platform or byo_keys)."""
        await self._ensure_transport()
        return await self.external_api_keys.get_mode()
    
    async def set_api_key_mode(self, mode: Union[str, ApiKeyMode]):
        """Set the API key mode (platform or byo_keys)."""
        await self._ensure_transport()
        return await self.external_api_keys.set_mode(mode)
    
    async def _create_stream_generator(
        self,
        *,
        input_data: Union[str, Dict[str, str], List[Dict[str, str]]],
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> AsyncGenerator[ProgressEntry, None]:
        # Transport is ensured by the caller (invoke_stream)
        # Get effective user_id (from parameter or scoped client)
        effective_user_id = user_id or self._scoped_user_id

        # Validate scope and user_id
        if scope == Scope.USER and not effective_user_id:
            raise MissingUserId()
        if scope == Scope.TENANT and effective_user_id:
            raise TenantScopeUserIdConflict()

        # Warn about tenant scope usage
        if scope == Scope.TENANT:
            await self._transport.warn_tenant_scope()

        # Convert input to messages format
        formatted_messages = self._convert_to_messages_format(input_data)

        # Create the response
        response = await self.responses.create(
            messages=formatted_messages,
            user_id=effective_user_id,
            thread_id=thread_id,
            idempotency_key=idempotency_key,
            options=options,
        )

        # Stream updates until completion
        last_message_count = 0

        while True:
            try:
                # Try long-polling first for efficiency
                current = await self.responses.get(response.response_id, wait=wait_timeout)
            except Exception as e:
                # Fall back to regular polling if long-polling fails
                logger.debug(f"Long-polling failed, falling back to regular polling: {type(e).__name__}: {e}")
                current = await self.responses.get(response.response_id)

            # Yield only new progress entries
            current_msg_count = len(current.progress) if current.progress else 0
            
            if current_msg_count > last_message_count and current.progress:
                # Yield each new progress entry individually
                for i in range(last_message_count, current_msg_count):
                    yield current.progress[i]
                last_message_count = current_msg_count

            # Check if completed
            if current.status in ("succeeded", "failed", "cancelled"):
                # Yield final completion entry with output_text if succeeded
                if current.status == "succeeded" and current.output_text:
                    from datetime import datetime
                    final_entry = ProgressEntry(
                        ts=current.completed_at or datetime.now(),
                        state="completed",
                        message="Task completed successfully",
                        output_text=current.output_text
                    )
                    yield final_entry
                
                logger.info(
                    f"Response {response.response_id} completed with status: {current.status}",
                    extra={
                        "response_id": str(response.response_id),
                        "status": current.status,
                    },
                )
                break

            # Wait before next poll
            await asyncio.sleep(poll_interval)
            
    async def _invoke_async(
        self,
        *,
        input_data: Union[str, Dict[str, str], List[Dict[str, str]]],
        user_id: Optional[str] = None,
        scope: Optional[Scope] = None,
        thread_id: Optional[str] = None,
        idempotency_key: Optional[str] = None,
        wait: bool = True,
        progress_callback: Optional[Callable[[ResponseObject], None]] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
        **options,
    ) -> ResponseObject:
        # Transport is ensured by the caller (invoke)
        # Get effective user_id (from parameter or scoped client)
        effective_user_id = user_id or self._scoped_user_id

        # Validate scope and user_id
        if scope == Scope.USER and not effective_user_id:
            raise MissingUserId()
        if scope == Scope.TENANT and effective_user_id:
            raise TenantScopeUserIdConflict()

        # Warn about tenant scope usage
        if scope == Scope.TENANT:
            await self._transport.warn_tenant_scope()

        # Convert input to messages format
        formatted_messages = self._convert_to_messages_format(input_data)

        # Create the response
        response = await self.responses.create(
            messages=formatted_messages,
            user_id=effective_user_id,
            thread_id=thread_id,
            idempotency_key=idempotency_key,
            options=options,
        )

        # Wait for completion if requested
        if wait:
            final_response = await self._poll_for_completion(
                response.response_id,
                progress_callback=progress_callback,
                poll_interval=poll_interval,
                wait_timeout=wait_timeout,
            )
            logger.info(
                f"Response {response.response_id} completed with status: {final_response.status}",
                extra={
                    "response_id": str(response.response_id),
                    "status": final_response.status,
                },
            )
            return final_response

        return response

    async def _poll_for_completion(
        self,
        response_id: str,
        *,
        progress_callback: Optional[Callable[[ResponseObject], None]] = None,
        poll_interval: float = DEFAULT_POLL_INTERVAL,
        wait_timeout: Optional[float] = LONG_POLL_TIMEOUT,
    ) -> ResponseObject:
        update_channel = asyncio.Queue(maxsize=1)
        final_response = None
        
        # Use the provided progress callback (can be None)
        callback = progress_callback
        
        async def _invoke_callback(callback_fn: Callable, response: ResponseObject) -> None:
            try:
                if inspect.iscoroutinefunction(callback_fn):
                    await callback_fn(response)
                else:
                    callback_fn(response)
            except Exception as e:
                logger.warning(f"Progress callback failed: {type(e).__name__}: {e}", 
                              extra={"callback_type": type(callback_fn).__name__})
        
        # Update processor task - processes updates sequentially
        async def update_processor():
            last_seen = None
            while True:
                try:
                    update = await update_channel.get()
                    if update is None:  # Sentinel to stop
                        break
                    
                    # Only process if newer than last seen (prevent out-of-order processing)
                    current_msg_count = len(update.progress) if update.progress else 0
                    last_msg_count = len(last_seen.progress) if last_seen and last_seen.progress else -1
                    
                    if current_msg_count >= last_msg_count:
                        if callback:
                            await _invoke_callback(callback, update)
                        last_seen = update
                        
                except Exception as e:
                    logger.warning(f"Update processor failed: {type(e).__name__}: {e}")
                finally:
                    update_channel.task_done()
        
        # Start update processor
        processor_task = asyncio.create_task(update_processor())
        
        try:
            last_message_count = 0
            
            while True:
                try:
                    # Try long-polling first for efficiency
                    current = await self.responses.get(response_id, wait=wait_timeout)
                except Exception as e:
                    # Fall back to regular polling if long-polling fails
                    logger.debug(f"Long-polling failed, falling back to regular polling: {type(e).__name__}: {e}")
                    current = await self.responses.get(response_id)
                
                # Check if we should emit progress update
                current_msg_count = len(current.progress) if current.progress else 0
                
                should_emit = (
                    current_msg_count != last_message_count or
                    current.status in ("succeeded", "failed", "cancelled")
                )
                
                if should_emit and callback:
                    # Use non-blocking put with maxsize=1 to prevent queue buildup
                    try:
                        update_channel.put_nowait(current)
                    except asyncio.QueueFull:
                        # Skip this update if queue is full (prevents slowdown)
                        logger.debug("Progress update skipped - processor busy")
                
                # Update tracking variables
                last_message_count = current_msg_count
                
                # Check if completed
                if current.status in ("succeeded", "failed", "cancelled"):
                    final_response = current
                    break
                
                # Wait before next poll
                await asyncio.sleep(poll_interval)
        
        finally:
            # Clean shutdown of update processor
            await update_channel.put(None)  # Sentinel to stop processor
            await processor_task
            
            # Default progress callback handles its own newlines
        
        return final_response
    
    def _create_simple_progress_callback(self) -> Callable[[ResponseObject], None]:
        """Create a simple progress callback that prints status and messages."""
        last_status = None
        seen_messages = set()
        
        def progress_callback(response: ResponseObject) -> None:
            nonlocal last_status, seen_messages
            
            current_status = response.status
            
            # Print status if it changed
            if current_status != last_status:
                # print(f"Status: {current_status}", flush=True)
                last_status = current_status
            
            # Print all new progress messages
            if response.progress:
                for entry in response.progress:
                    # Create a unique key for this message
                    message_key = f"{entry.state}:{entry.message}"
                    if message_key not in seen_messages:
                        print(f"{entry.state.upper()}: {entry.message}", flush=True)
                        seen_messages.add(message_key)
        
        return progress_callback
    
    def _resolve_input_parameters(
        self,
        messages: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        task: Union[str, Dict[str, str], List[Dict[str, str]]] = None,
        prompt: str = None,
    ) -> Union[str, Dict[str, str], List[Dict[str, str]]]:
        """Resolve input parameters with proper precedence and deprecation warnings."""
        # Count non-None parameters
        provided_params = sum(1 for param in [messages, task, prompt] if param is not None)
        
        if provided_params == 0:
            raise ValueError("Must provide one of: messages, task, or prompt parameter")
        
        if provided_params > 1:
            raise ValueError("Cannot provide multiple input parameters. Use only one of: messages, task, or prompt")
        
        # Handle deprecation warning for task parameter
        if task is not None:
            import warnings
            warnings.warn(
                "The 'task' parameter is deprecated. Use 'messages' or 'prompt' instead.",
                DeprecationWarning,
                stacklevel=3
            )
            return task
        
        # Return the provided parameter
        return messages if messages is not None else prompt
    
    def _convert_to_messages_format(
        self, 
        input_data: Union[str, Dict[str, str], List[Dict[str, str]]]
    ) -> List[Dict[str, str]]:
        """Convert input to standardized messages format."""
        if isinstance(input_data, str):
            return [{"role": "user", "content": input_data}]
        elif isinstance(input_data, dict):
            # Handle single dict message (common mistake)
            return [input_data]
        else:
            return input_data
    
