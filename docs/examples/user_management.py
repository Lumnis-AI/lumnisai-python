"""
User Management API Example

This example demonstrates how to use the User Management API to:
- Create users
- Retrieve users by ID or email
- Update user information
- Delete users
- List all users with pagination
- Integrate users with threads and responses

The SDK provides a simple flattened API for user management:
client.create_user(), client.get_user(), client.update_user(), etc.

Authentication: Requires API key via environment variable or direct initialization
"""

import asyncio
import os
from uuid import UUID

from lumnisai import AsyncClient, Client


async def async_user_management_example():
    """Async example of user management operations"""
    
    # Initialize the client (using TENANT scope for admin operations)
    from lumnisai.types import Scope
    client = AsyncClient(api_key=os.getenv("LUMNISAI_API_KEY"), scope=Scope.TENANT)
    
    async with client:
        print("=== User Management Example (Async) ===\n")
        
        # 1. Create a new user (using flattened API)
        print("1. Creating a new user...")
        import time
        timestamp = int(time.time())
        user = await client.create_user(
            email=f"john.doe.{timestamp}@example.com",
            first_name="John",
            last_name="Doe"
        )
        print(f"Created user: {user.email} (ID: {user.id})")
        print(f"Tenant ID: {user.tenant_id}")
        print(f"Active: {user.is_active}")
        print(f"Created at: {user.created_at}")
        
        # 2. Get user by ID
        print("\n2. Retrieving user by ID...")
        user_by_id = await client.get_user(user.id)
        print(f"Retrieved by ID: {user_by_id.email}")
        
        # 3. Get user by email
        print("\n3. Retrieving user by email...")
        user_by_email = await client.get_user(user.email)
        print(f"Retrieved by email: {user_by_email.id}")
        
        # 4. Update user information
        print("\n4. Updating user information...")
        updated_user = await client.update_user(
            user.id,
            first_name="Jane",
            last_name="Smith"
        )
        print(f"Updated user: {updated_user.first_name} {updated_user.last_name}")
        print(f"Email (unchanged): {updated_user.email}")
        
        # 5. Create multiple users for list demonstration
        print("\n5. Creating additional users...")
        users_data = [
            (f"user1.{timestamp}@example.com", "Alice", "Smith"),
            (f"user2.{timestamp}@example.com", "Bob", "Johnson"),
            (f"user3.{timestamp}@example.com", "Charlie", "Williams"),
        ]
        
        for email, first_name, last_name in users_data:
            await client.create_user(
                email=email,
                first_name=first_name,
                last_name=last_name
            )
        print(f"Created {len(users_data)} additional users")
        
        # 6. List users with pagination
        print("\n6. Listing users with pagination...")
        users_page1 = await client.list_users(page=1, page_size=2)
        print(f"Page 1 ({users_page1.pagination.total} total users):")
        for user in users_page1.users:
            print(f"  - {user.email} ({user.first_name} {user.last_name})")
        
        if users_page1.pagination.has_next:
            users_page2 = await client.list_users(page=2, page_size=2)
            print(f"\nPage 2:")
            for user in users_page2.users:
                print(f"  - {user.email} ({user.first_name} {user.last_name})")
        
        # 7. Delete a user (cascades to all associated data)
        print("\n7. Deleting a user...")
        await client.delete_user(f"user1.{timestamp}@example.com")
        print(f"User user1.{timestamp}@example.com deleted successfully")
        
        # Verify deletion
        users_after_deletion = await client.list_users()
        print(f"Remaining users: {users_after_deletion.pagination.total}")


def sync_user_management_example():
    """Sync example of user management operations"""
    
    # Initialize the client (using TENANT scope for admin operations)
    from lumnisai.types import Scope
    client = Client(api_key=os.getenv("LUMNISAI_API_KEY"), scope=Scope.TENANT)
    
    print("=== User Management Example (Sync) ===\n")
    
    # 1. Create a new user (using flattened API)
    print("1. Creating a new user...")
    import time
    timestamp = int(time.time())
    user = client.create_user(
        email=f"sync.user.{timestamp}@example.com",
        first_name="Sync",
        last_name="User"
    )
    print(f"Created user: {user.email} (ID: {user.id})")
    
    # 2. Update the user
    print("\n2. Updating user...")
    updated_user = client.update_user(
        user.id,
        first_name="Updated"
    )
    print(f"Updated name: {updated_user.first_name} {updated_user.last_name}")
    
    # 3. List all users
    print("\n3. Listing all users...")
    users = client.list_users(page_size=10)
    for user in users.users:
        print(f"  - {user.email}")
    
    # 4. Delete the user
    print("\n4. Cleaning up...")
    client.delete_user(user.id)
    print("User deleted successfully")
    
    client.close()


async def bulk_user_import_example():
    """Example of bulk user import"""
    
    from lumnisai.types import Scope
    client = AsyncClient(api_key=os.getenv("LUMNISAI_API_KEY"), scope=Scope.TENANT)
    
    async with client:
        print("=== Bulk User Import Example ===\n")
        
        # List of users to import
        import time
        timestamp = int(time.time())
        users_to_import = [
            {"email": f"import1.{timestamp}@example.com", "first_name": "Import", "last_name": "One"},
            {"email": f"import2.{timestamp}@example.com", "first_name": "Import", "last_name": "Two"},
            {"email": f"import3.{timestamp}@example.com", "first_name": "Import", "last_name": "Three"},
        ]
        
        created_users = []
        failed_imports = []
        
        for user_data in users_to_import:
            try:
                user = await client.create_user(**user_data)
                created_users.append(user)
                print(f"✓ Imported: {user.email}")
            except Exception as e:
                failed_imports.append((user_data['email'], str(e)))
                print(f"✗ Failed: {user_data['email']} - {e}")
        
        print(f"\nImport complete: {len(created_users)} successful, {len(failed_imports)} failed")


async def user_lifecycle_example():
    """Example showing complete user lifecycle"""
    
    from lumnisai.types import Scope
    client = AsyncClient(api_key=os.getenv("LUMNISAI_API_KEY"), scope=Scope.TENANT)
    
    async with client:
        print("=== User Lifecycle Example ===\n")
        
        # 1. User signs up
        print("1. User signs up...")
        import time
        timestamp = int(time.time())
        user = await client.create_user(
            email=f"lifecycle.{timestamp}@example.com",
            first_name="Test",
            last_name="User"
        )
        print(f"Welcome {user.first_name}!")
        print(f"User ID: {user.id}")
        print(f"Email: {user.email}")
        
        # 2. User updates their profile
        print("\n2. User updates profile...")
        updated_user = await client.update_user(
            user.id,
            first_name="Advanced",
            last_name="User"
        )
        print(f"Profile updated: {updated_user.first_name} {updated_user.last_name}")
        
        # 3. Check user details
        print("\n3. Retrieving user details...")
        retrieved_user = await client.get_user(user.id)
        print(f"User status: {'Active' if retrieved_user.is_active else 'Inactive'}")
        print(f"Member since: {retrieved_user.created_at}")
        
        # 4. User requests data deletion (GDPR)
        print("\n4. User requests account deletion...")
        await client.delete_user(user.id)
        print("User account and all associated data deleted")


def main():
    """Run examples based on command line argument or environment"""
    import sys
    
    if len(sys.argv) > 1:
        example = sys.argv[1]
        
        if example == "async":
            asyncio.run(async_user_management_example())
        elif example == "sync":
            sync_user_management_example()
        elif example == "bulk":
            asyncio.run(bulk_user_import_example())
        elif example == "lifecycle":
            asyncio.run(user_lifecycle_example())
        else:
            print("Unknown example. Choose: async, sync, bulk, or lifecycle")
    else:
        # Default to async example
        asyncio.run(async_user_management_example())


if __name__ == "__main__":
    main()