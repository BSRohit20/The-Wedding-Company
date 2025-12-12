"""
Database connection and management.
Handles MongoDB connections for both master database and dynamic organization collections.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from typing import Optional
from app.config import settings


class DatabaseManager:
    """Manages MongoDB connections and database operations."""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.master_db = None
    
    async def connect_to_database(self):
        """Establish connection to MongoDB."""
        try:
            self.client = AsyncIOMotorClient(settings.MONGODB_URL, serverSelectionTimeoutMS=5000)
            # Test the connection
            await self.client.admin.command('ping')
            self.master_db = self.client[settings.MASTER_DB_NAME]
            print(f"Connected to MongoDB at {settings.MONGODB_URL}")
        except Exception as e:
            print(f"Failed to connect to MongoDB: {e}")
            print("Warning: Running without database connection")
    
    async def close_database_connection(self):
        """Close MongoDB connection."""
        if self.client:
            self.client.close()
            print("Closed MongoDB connection")
    
    def get_master_db(self):
        """Get the master database instance."""
        return self.master_db
    
    def get_organization_collection(self, collection_name: str):
        """
        Get a specific organization's collection from the master database.
        
        Args:
            collection_name: Name of the organization collection
            
        Returns:
            MongoDB collection instance
        """
        return self.master_db[collection_name]
    
    async def create_organization_collection(self, collection_name: str):
        """
        Create a new collection for an organization.
        
        Args:
            collection_name: Name of the collection to create
        """
        # MongoDB creates collections automatically on first insert
        # But we can explicitly create it with validation schema if needed
        collection = self.master_db[collection_name]
        
        # Create a basic index for better performance
        await collection.create_index("created_at")
        
        return collection
    
    async def delete_organization_collection(self, collection_name: str):
        """
        Delete an organization's collection.
        
        Args:
            collection_name: Name of the collection to delete
        """
        await self.master_db[collection_name].drop()
    
    async def collection_exists(self, collection_name: str) -> bool:
        """
        Check if a collection exists.
        
        Args:
            collection_name: Name of the collection to check
            
        Returns:
            True if collection exists, False otherwise
        """
        collections = await self.master_db.list_collection_names()
        return collection_name in collections


# Global database manager instance
db_manager = DatabaseManager()


def get_database_manager() -> DatabaseManager:
    """Dependency injection for database manager."""
    return db_manager
