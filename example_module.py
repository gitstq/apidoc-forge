#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Example module demonstrating APIDoc Forge capabilities.

This module showcases various Python constructs that APIDoc Forge can document,
including functions, classes, async functions, and different docstring styles.
"""

from typing import Optional, List, Dict, Any, Union
from dataclasses import dataclass
from enum import Enum


# Module-level constants
DEFAULT_TIMEOUT = 30
MAX_RETRIES = 3
API_VERSION = "1.0.0"


class StatusCode(Enum):
    """HTTP status codes used by the API."""
    OK = 200
    CREATED = 201
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    NOT_FOUND = 404
    SERVER_ERROR = 500


@dataclass
class User:
    """Represents a user in the system.
    
    Attributes:
        id: Unique identifier for the user.
        name: Full name of the user.
        email: Email address of the user.
        is_active: Whether the user account is active.
    """
    id: int
    name: str
    email: str
    is_active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert user to dictionary representation.
        
        Returns:
            Dictionary containing user data.
        """
        return {
            "id": self.id,
            "name": self.name,
            "email": self.email,
            "is_active": self.is_active
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "User":
        """Create a User instance from a dictionary.
        
        Args:
            data: Dictionary containing user data.
        
        Returns:
            A new User instance.
        """
        return cls(
            id=data["id"],
            name=data["name"],
            email=data["email"],
            is_active=data.get("is_active", True)
        )


class UserManager:
    """Manages user operations and data persistence.
    
    This class provides methods for creating, reading, updating, and deleting
    user records. It handles validation and error handling automatically.
    
    Attributes:
        users: Dictionary mapping user IDs to User objects.
        auto_save: Whether to automatically save changes to storage.
    
    Example:
        >>> manager = UserManager(auto_save=True)
        >>> user = manager.create_user("John Doe", "john@example.com")
        >>> print(user.id)
        1
    """
    
    def __init__(self, auto_save: bool = False):
        """Initialize the UserManager.
        
        Args:
            auto_save: Whether to automatically save changes.
        """
        self.users: Dict[int, User] = {}
        self.auto_save = auto_save
        self._next_id = 1
    
    def create_user(self, name: str, email: str, is_active: bool = True) -> User:
        """Create a new user in the system.
        
        Args:
            name: Full name of the user.
            email: Valid email address.
            is_active: Whether the user should be active (default: True).
        
        Returns:
            The newly created User object.
        
        Raises:
            ValueError: If email is invalid or name is empty.
        
        Example:
            >>> manager = UserManager()
            >>> user = manager.create_user("Jane Doe", "jane@example.com")
            >>> user.name
            'Jane Doe'
        """
        if not name:
            raise ValueError("Name cannot be empty")
        if "@" not in email:
            raise ValueError("Invalid email address")
        
        user = User(
            id=self._next_id,
            name=name,
            email=email,
            is_active=is_active
        )
        self.users[user.id] = user
        self._next_id += 1
        
        if self.auto_save:
            self._save_to_storage()
        
        return user
    
    def get_user(self, user_id: int) -> Optional[User]:
        """Retrieve a user by their ID.
        
        Args:
            user_id: The unique identifier of the user.
        
        Returns:
            The User object if found, None otherwise.
        """
        return self.users.get(user_id)
    
    def update_user(self, user_id: int, **kwargs) -> User:
        """Update user information.
        
        Args:
            user_id: The ID of the user to update.
            **kwargs: Fields to update (name, email, is_active).
        
        Returns:
            The updated User object.
        
        Raises:
            KeyError: If user_id is not found.
        """
        if user_id not in self.users:
            raise KeyError(f"User {user_id} not found")
        
        user = self.users[user_id]
        for key, value in kwargs.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        if self.auto_save:
            self._save_to_storage()
        
        return user
    
    def delete_user(self, user_id: int) -> bool:
        """Delete a user from the system.
        
        Args:
            user_id: The ID of the user to delete.
        
        Returns:
            True if deleted, False if user didn't exist.
        """
        if user_id in self.users:
            del self.users[user_id]
            if self.auto_save:
                self._save_to_storage()
            return True
        return False
    
    def list_users(self, active_only: bool = False) -> List[User]:
        """Get a list of all users.
        
        Args:
            active_only: If True, return only active users.
        
        Returns:
            List of User objects.
        """
        users = list(self.users.values())
        if active_only:
            users = [u for u in users if u.is_active]
        return users
    
    def _save_to_storage(self) -> None:
        """Internal method to save users to persistent storage."""
        # Implementation would go here
        pass


def calculate_statistics(data: List[float]) -> Dict[str, float]:
    """Calculate basic statistics for a dataset.
    
    Args:
        data: List of numeric values.
    
    Returns:
        Dictionary containing mean, median, min, max, and std.
    
    Raises:
        ValueError: If data is empty.
    
    Example:
        >>> stats = calculate_statistics([1, 2, 3, 4, 5])
        >>> stats["mean"]
        3.0
    """
    if not data:
        raise ValueError("Cannot calculate statistics for empty dataset")
    
    import statistics
    
    return {
        "mean": statistics.mean(data),
        "median": statistics.median(data),
        "min": min(data),
        "max": max(data),
        "std": statistics.stdev(data) if len(data) > 1 else 0.0
    }


def format_response(data: Any, status: StatusCode = StatusCode.OK) -> Dict[str, Any]:
    """Format data into a standard API response.
    
    Args:
        data: The data to include in the response.
        status: HTTP status code (default: StatusCode.OK).
    
    Returns:
        Formatted response dictionary.
    """
    return {
        "success": status.value < 400,
        "status_code": status.value,
        "data": data
    }


async def fetch_user_data(user_id: int, include_metadata: bool = False) -> Dict[str, Any]:
    """Asynchronously fetch user data from external API.
    
    Args:
        user_id: The ID of the user to fetch.
        include_metadata: Whether to include additional metadata.
    
    Returns:
        Dictionary containing user data.
    
    Raises:
        ConnectionError: If the API request fails.
    
    Note:
        This is an async function and must be awaited.
    """
    # Simulated async API call
    import asyncio
    await asyncio.sleep(0.1)
    
    return {
        "id": user_id,
        "name": f"User {user_id}",
        "metadata": {} if not include_metadata else {"created": "2024-01-01"}
    }


def process_items(
    items: List[str],
    processor: callable = str.upper,
    *filters: str,
    skip_errors: bool = True,
    **options
) -> List[str]:
    """Process a list of items with various options.
    
    Demonstrates complex parameter handling including:
    - Regular arguments
    - Default values with callables
    - *args for filters
    - **kwargs for options
    - Keyword-only arguments
    
    Args:
        items: List of items to process.
        processor: Function to apply to each item (default: str.upper).
        *filters: Optional filters to exclude certain items.
        skip_errors: Whether to skip items that cause errors.
        **options: Additional processing options.
    
    Returns:
        List of processed items.
    """
    results = []
    
    for item in items:
        try:
            # Skip if matches any filter
            if any(f in item for f in filters):
                continue
            
            processed = processor(item)
            results.append(processed)
        except Exception as e:
            if not skip_errors:
                raise
    
    return results


# Type aliases
UserList = List[User]
UserDict = Dict[int, User]
OptionalUser = Optional[User]
