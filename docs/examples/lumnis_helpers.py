"""
LumnisAI Helper Utilities

This module provides helper functions and classes to simplify common LumnisAI operations
with better error handling, retry logic, and developer-friendly interfaces.
"""

import asyncio
import json
import os
from typing import Dict, Any, Optional, List, Union
from dataclasses import dataclass
from datetime import datetime
import logging

try:
    import lumnisai
    from lumnisai import AsyncClient, ApiProvider
    from pydantic import BaseModel
except ImportError as e:
    raise ImportError(f"LumnisAI not installed: {e}")

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SetupResult:
    """Result of setup operations"""
    success: bool
    user: Optional[Any] = None
    api_keys: List[str] = None
    apps: List[str] = None
    connections: Optional[Any] = None
    errors: List[str] = None
    
    def __post_init__(self):
        if self.api_keys is None:
            self.api_keys = []
        if self.apps is None:
            self.apps = []
        if self.errors is None:
            self.errors = []


class QuickSetup:
    """Simplified setup class for LumnisAI"""
    
    def __init__(self, client: Optional[AsyncClient] = None):
        self.client = client or AsyncClient()
        self._ready = False
        self._user_email = None
        
    async def initialize(
        self,
        user_email: str,
        first_name: str = "Developer",
        last_name: str = "User",
        apps: Optional[List[str]] = None,
        api_keys: Optional[Dict[str, str]] = None,
        model_preferences: Optional[Dict[str, Dict[str, str]]] = None,
        verbose: bool = True
    ) -> SetupResult:
        """Initialize LumnisAI with all necessary setup"""
        if verbose:
            print("🚀 Initializing LumnisAI...")
        
        # Set defaults
        apps = apps or ["github", "gmail"]
        api_keys = api_keys or {
            "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY"),
            "EXA_API_KEY": os.getenv("EXA_API_KEY")
        }
        
        result = SetupResult(success=False)
        
        try:
            # Setup user
            if verbose:
                print("👤 Setting up user...")
            result.user = await self._setup_user(user_email, first_name, last_name)
            self._user_email = user_email
            if verbose:
                print(f"   ✅ User ready: {user_email}")
            
            # Setup API keys
            if verbose:
                print("🔑 Adding API keys...")
            for key_name, key_value in api_keys.items():
                if key_value:
                    try:
                        await self._add_api_key(key_name, key_value)
                        result.api_keys.append(key_name)
                        if verbose:
                            print(f"   ✅ {key_name} added")
                    except Exception as e:
                        error_msg = f"API key {key_name}: {str(e)}"
                        result.errors.append(error_msg)
                        if verbose:
                            print(f"   ⚠️  {error_msg}")
            
            # Enable apps
            if verbose:
                print("🔌 Enabling apps...")
            for app in apps:
                try:
                    await self._enable_app(app)
                    result.apps.append(app)
                    if verbose:
                        print(f"   ✅ {app} enabled")
                except Exception as e:
                    error_msg = f"App {app}: {str(e)}"
                    result.errors.append(error_msg)
                    if verbose:
                        print(f"   ⚠️  {error_msg}")
            
            result.success = True
            self._ready = True
            
            if verbose:
                print("🎉 Setup complete!")
                
        except Exception as e:
            error_msg = f"Setup failed: {str(e)}"
            result.errors.append(error_msg)
            if verbose:
                print(f"❌ {error_msg}")
        
        return result
    
    async def _setup_user(self, email: str, first_name: str, last_name: str):
        """Setup user, create if needed"""
        users = await self.client.list_users(page_size=50)
        existing_user = next((u for u in users.users if u.email == email), None)
        
        if existing_user:
            return existing_user
        else:
            return await self.client.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name
            )
    
    async def _add_api_key(self, key_name: str, key_value: str):
        """Add API key with proper error handling"""
        try:
            provider = getattr(ApiProvider, key_name)
            await self.client.add_api_key(provider, key_value)
        except AttributeError:
            raise ValueError(f"Unknown API provider: {key_name}")
        except Exception as e:
            raise Exception(f"Failed to add API key: {str(e)}")
    
    async def _enable_app(self, app_name: str):
        """Enable app with proper error handling"""
        try:
            is_enabled = await self.client.is_app_enabled(app_name)
            if not is_enabled:
                await self.client.set_app_enabled(app_name, enabled=True)
        except Exception as e:
            raise Exception(f"Failed to enable app: {str(e)}")
    
    def get_user_client(self) -> AsyncClient:
        """Get user-scoped client"""
        if not self._ready or not self._user_email:
            raise ValueError("Setup not complete - call initialize() first")
        return self.client.for_user(self._user_email)
    
    @property
    def is_ready(self) -> bool:
        """Check if setup is complete"""
        return self._ready


async def safe_invoke(
    client: AsyncClient,
    prompt: str,
    user_id: Optional[str] = None,
    max_retries: int = 3,
    timeout: int = 120,
    **kwargs
) -> Optional[Any]:
    """Safe invoke with retry logic and timeout"""
    for attempt in range(max_retries):
        try:
            if user_id:
                kwargs['user_id'] = user_id
            
            response = await client.invoke(prompt, **kwargs)
            return response
            
        except asyncio.TimeoutError:
            logger.warning(f"Attempt {attempt + 1} timed out after {timeout}s")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            logger.warning(f"Attempt {attempt + 1} failed: {str(e)}")
            if attempt < max_retries - 1:
                await asyncio.sleep(2 ** attempt)
            else:
                logger.error(f"All {max_retries} attempts failed. Last error: {str(e)}")
    
    return None


def create_client(user_email: Optional[str] = None) -> AsyncClient:
    """Create a LumnisAI client with optional user scoping"""
    client = AsyncClient()
    if user_email:
        return client.for_user(user_email)
    return client 