import asyncio
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable, ContextManager, Dict, Iterator, List, Literal, Optional, TypeVar, Union, overload
from uuid import UUID

from .async_client import AsyncClient
from .models import ResponseObject, ProgressEntry
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
            import sys
            import inspect
            
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
                    method_call += ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
                
                method_call += ")"
            else:
                method_call = "client.invoke(..., stream=True)"
            
            error_msg = (
                "Cannot use synchronous Client with streaming in an async environment.\n\n"
            )
            
            if 'ipykernel' in sys.modules or 'IPython' in sys.modules:
                error_msg += (
                    "📓 For Jupyter/Colab notebooks, use AsyncClient instead:\n\n"
                    f"    client = lumnisai.AsyncClient()\n"
                    f"    async for update in client.invoke(..., stream=True):\n"
                    f"        print(update.status)\n"
                )
            else:
                error_msg += (
                    "Use AsyncClient for streaming:\n\n"
                    f"    async with lumnisai.AsyncClient() as client:\n"
                    f"        async for update in client.invoke(..., stream=True):\n"
                    f"            print(update.status)\n"
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
            import sys
            import inspect
            
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
                    method_call += ", ".join(f"{k}={repr(v)}" for k, v in kwargs.items())
                
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
        api_key: Optional[str] = None,
        base_url: Optional[str] = None,
        tenant_id: Optional[str] = None,
        timeout: float = 30.0,
        max_retries: int = 3,
        scope: Scope = Scope.USER,
        _scoped_user_id: Optional[str] = None,
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
    def tenant(self):
        return SyncResourceProxy(self._async_client.tenant)

    @property
    def users(self):
        return SyncResourceProxy(self._async_client.users)

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
    def as_user(self, user_id: str) -> ContextManager["Client"]:
        client = self.for_user(user_id)
        try:
            yield client
        finally:
            client.close()

    @overload
    def invoke(
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
        poll_interval: float = 2.0,
        **options,
    ) -> ResponseObject: ...

    @overload
    def invoke(
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
        poll_interval: float = 2.0,
        **options,
    ) -> Iterator[ProgressEntry]: ...

    def invoke(
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
        poll_interval: float = 2.0,
        **options,
    ) -> Union[ResponseObject, Iterator[ProgressEntry]]:
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
                **options,
            )


    # Direct resource access methods for flattened API
    def get_response(self, response_id: str, *, wait: Optional[float] = None) -> ResponseObject:
        get_response_async = sync_wrapper(self._async_client.get_response)
        return get_response_async(response_id, wait=wait)

    def list_responses(self, *, user_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None):
        list_responses_async = sync_wrapper(self._async_client.list_responses)
        return list_responses_async(user_id=user_id, limit=limit, cursor=cursor)

    def cancel_response(self, response_id: str) -> ResponseObject:
        cancel_response_async = sync_wrapper(self._async_client.cancel_response)
        return cancel_response_async(response_id)

    def list_threads(self, *, user_id: Optional[str] = None, limit: int = 50, cursor: Optional[str] = None):
        list_threads_async = sync_wrapper(self._async_client.list_threads)
        return list_threads_async(user_id=user_id, limit=limit, cursor=cursor)

    def get_thread(self, thread_id: str):
        get_thread_async = sync_wrapper(self._async_client.get_thread)
        return get_thread_async(thread_id)

    def create_thread(self, *, user_id: Optional[str] = None, title: Optional[str] = None):
        create_thread_async = sync_wrapper(self._async_client.create_thread)
        return create_thread_async(user_id=user_id, title=title)

    def delete_thread(self, thread_id: str):
        delete_thread_async = sync_wrapper(self._async_client.delete_thread)
        return delete_thread_async(thread_id)
    
    # User management flattened methods
    def create_user(self, *, email: str, first_name: Optional[str] = None, last_name: Optional[str] = None):
        create_user_async = sync_wrapper(self._async_client.create_user)
        return create_user_async(email=email, first_name=first_name, last_name=last_name)
    
    def get_user(self, user_identifier: Union[str, UUID]):
        get_user_async = sync_wrapper(self._async_client.get_user)
        return get_user_async(user_identifier)
    
    def update_user(self, user_identifier: Union[str, UUID], *, first_name: Optional[str] = None, last_name: Optional[str] = None):
        update_user_async = sync_wrapper(self._async_client.update_user)
        return update_user_async(user_identifier, first_name=first_name, last_name=last_name)
    
    def delete_user(self, user_identifier: Union[str, UUID]):
        delete_user_async = sync_wrapper(self._async_client.delete_user)
        return delete_user_async(user_identifier)
    
    def list_users(self, *, page: int = 1, page_size: int = 20):
        list_users_async = sync_wrapper(self._async_client.list_users)
        return list_users_async(page=page, page_size=page_size)
    
    # External API Key helpers
    def add_api_key(self, provider: Union[str, ApiProvider], api_key: str):
        """Add an external API key for BYO keys mode."""
        add_api_key_async = sync_wrapper(self._async_client.add_api_key)
        return add_api_key_async(provider, api_key)
    
    def list_api_keys(self):
        """List all stored external API keys."""
        list_api_keys_async = sync_wrapper(self._async_client.list_api_keys)
        return list_api_keys_async()
    
    def get_api_key(self, key_id: Union[str, UUID]):
        """Get a specific external API key by ID."""
        get_api_key_async = sync_wrapper(self._async_client.get_api_key)
        return get_api_key_async(key_id)
    
    def delete_api_key(self, provider: Union[str, ApiProvider]):
        """Delete an external API key."""
        delete_api_key_async = sync_wrapper(self._async_client.delete_api_key)
        return delete_api_key_async(provider)
    
    def get_api_key_mode(self):
        """Get the current API key mode (platform or byo_keys)."""
        get_api_key_mode_async = sync_wrapper(self._async_client.get_api_key_mode)
        return get_api_key_mode_async()
    
    def set_api_key_mode(self, mode: Union[str, ApiKeyMode]):
        """Set the API key mode (platform or byo_keys)."""
        set_api_key_mode_async = sync_wrapper(self._async_client.set_api_key_mode)
        return set_api_key_mode_async(mode)