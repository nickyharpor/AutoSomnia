import logging
from typing import Any, Dict, List, Optional, Union, MutableMapping
from datetime import datetime
from contextlib import asynccontextmanager

import pymongo
from pymongo import MongoClient
from pymongo.collection import Collection
from pymongo.database import Database
from pymongo.errors import (
    ConnectionFailure,
    DuplicateKeyError,
    ServerSelectionTimeoutError
)
from bson import ObjectId
from bson.errors import InvalidId

logger = logging.getLogger(__name__)


class MongoDBManager:
    """
    MongoDB manager class for handling CRUD operations with best practices.
    
    Features:
    - Connection pooling and management
    - Automatic reconnection handling
    - Comprehensive error handling
    - Index management
    - Transaction support
    - Query optimization
    """

    def __init__(
        self,
        connection_string: str,
        database_name: str,
        max_pool_size: int = 100,
        min_pool_size: int = 0,
        server_selection_timeout_ms: int = 5000,
        connect_timeout_ms: int = 10000,
        socket_timeout_ms: int = 10000,
        max_idle_time_ms: int = 30000
    ):
        """
        Initialize MongoDB manager.
        
        Args:
            connection_string: MongoDB connection URI
            database_name: Name of the database to use
            max_pool_size: Maximum number of connections in the pool
            min_pool_size: Minimum number of connections in the pool
            server_selection_timeout_ms: Timeout for server selection
            connect_timeout_ms: Connection timeout
            socket_timeout_ms: Socket timeout
            max_idle_time_ms: Maximum idle time for connections
        """
        self.connection_string = connection_string
        self.database_name = database_name
        self._client: Optional[MongoClient] = None
        self._database: Optional[Database] = None
        
        # Connection configuration
        self.connection_config = {
            'maxPoolSize': max_pool_size,
            'minPoolSize': min_pool_size,
            'serverSelectionTimeoutMS': server_selection_timeout_ms,
            'connectTimeoutMS': connect_timeout_ms,
            'socketTimeoutMS': socket_timeout_ms,
            'maxIdleTimeMS': max_idle_time_ms,
            'retryWrites': True,
            'retryReads': True
        }
        
        logger.info(f"MongoDB manager initialized for database: {database_name}")

    def connect(self) -> None:
        """Establish connection to MongoDB."""
        try:
            self._client = MongoClient(self.connection_string, **self.connection_config)
            self._database = self._client[self.database_name]
            
            # Test connection
            self._client.admin.command('ping')
            logger.info("Successfully connected to MongoDB")
            
        except (ConnectionFailure, ServerSelectionTimeoutError) as e:
            logger.error(f"Failed to connect to MongoDB: {e}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error connecting to MongoDB: {e}")
            raise

    def disconnect(self) -> None:
        """Close MongoDB connection."""
        if self._client:
            self._client.close()
            self._client = None
            self._database = None
            logger.info("Disconnected from MongoDB")

    @property
    def client(self) -> MongoClient:
        """Get MongoDB client, connecting if necessary."""
        if not self._client:
            self.connect()
        return self._client

    @property
    def database(self) -> Database:
        """Get MongoDB database, connecting if necessary."""
        if not self._database:
            self.connect()
        return self._database

    def get_collection(self, collection_name: str) -> Collection:
        """
        Get a collection from the database.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            MongoDB collection object
        """
        return self.database[collection_name]

    # ==================== CRUD Operations ====================

    def insert_one(
        self, 
        collection_name: str, 
        document: Dict[str, Any],
        add_timestamps: bool = True
    ) -> str:
        """
        Insert a single document.
        
        Args:
            collection_name: Name of the collection
            document: Document to insert
            add_timestamps: Whether to add created_at/updated_at timestamps
            
        Returns:
            Inserted document ID as string
        """
        try:
            if add_timestamps:
                now = datetime.now()
                document['created_at'] = now
                document['updated_at'] = now
            
            collection = self.get_collection(collection_name)
            result = collection.insert_one(document)
            
            logger.info(f"Inserted document in {collection_name}: {result.inserted_id}")
            return str(result.inserted_id)
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error in {collection_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inserting document in {collection_name}: {e}")
            raise

    def insert_many(
        self, 
        collection_name: str, 
        documents: List[Dict[str, Any]],
        add_timestamps: bool = True,
        ordered: bool = False
    ) -> List[str]:
        """
        Insert multiple documents.
        
        Args:
            collection_name: Name of the collection
            documents: List of documents to insert
            add_timestamps: Whether to add created_at/updated_at timestamps
            ordered: Whether to perform ordered inserts
            
        Returns:
            List of inserted document IDs as strings
        """
        try:
            if add_timestamps:
                now = datetime.now()
                for doc in documents:
                    doc['created_at'] = now
                    doc['updated_at'] = now
            
            collection = self.get_collection(collection_name)
            result = collection.insert_many(documents, ordered=ordered)
            
            inserted_ids = [str(id_) for id_ in result.inserted_ids]
            logger.info(f"Inserted {len(inserted_ids)} documents in {collection_name}")
            return inserted_ids
            
        except DuplicateKeyError as e:
            logger.error(f"Duplicate key error in {collection_name}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error inserting documents in {collection_name}: {e}")
            raise

    def find_one(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any],
        projection: Optional[Dict[str, Any]] = None
    ) -> Optional[Dict[str, Any]]:
        """
        Find a single document.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter
            projection: Fields to include/exclude
            
        Returns:
            Found document or None
        """
        try:
            # Convert string ID to ObjectId if needed
            if '_id' in filter_dict and isinstance(filter_dict['_id'], str):
                try:
                    filter_dict['_id'] = ObjectId(filter_dict['_id'])
                except InvalidId:
                    logger.warning(f"Invalid ObjectId format: {filter_dict['_id']}")
                    return None
            
            collection = self.get_collection(collection_name)
            result = collection.find_one(filter_dict, projection)
            
            if result and '_id' in result:
                result['_id'] = str(result['_id'])
            
            return result
            
        except Exception as e:
            logger.error(f"Error finding document in {collection_name}: {e}")
            raise

    def find_many(
        self,
        collection_name: str,
        filter_dict: Dict[str, Any] = None,
        projection: Optional[Dict[str, Any]] = None,
        sort: Optional[tuple] = None,
        limit: Optional[int] = None,
        skip: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Find multiple documents.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter (empty dict for all documents)
            projection: Fields to include/exclude
            sort: Sort specification [(field, direction), ...]
            limit: Maximum number of documents to return
            skip: Number of documents to skip
            
        Returns:
            List of found documents
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            
            collection = self.get_collection(collection_name)
            cursor = collection.find(filter_dict, projection)
            
            if sort:
                cursor = cursor.sort(sort)
            if skip:
                cursor = cursor.skip(skip)
            if limit:
                cursor = cursor.limit(limit)
            
            results = list(cursor)
            
            # Convert ObjectId to string
            for doc in results:
                if '_id' in doc:
                    doc['_id'] = str(doc['_id'])
            
            logger.info(f"Found {len(results)} documents in {collection_name}")
            return results
            
        except Exception as e:
            logger.error(f"Error finding documents in {collection_name}: {e}")
            raise

    def update_one(
        self,
        collection_name: str,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        upsert: bool = False,
        add_timestamp: bool = True
    ) -> Dict[str, Any]:
        """
        Update a single document.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter
            update_dict: Update operations
            upsert: Whether to insert if document doesn't exist
            add_timestamp: Whether to add updated_at timestamp
            
        Returns:
            Update result information
        """
        try:
            # Convert string ID to ObjectId if needed
            if '_id' in filter_dict and isinstance(filter_dict['_id'], str):
                try:
                    filter_dict['_id'] = ObjectId(filter_dict['_id'])
                except InvalidId:
                    logger.warning(f"Invalid ObjectId format: {filter_dict['_id']}")
                    return {'matched_count': 0, 'modified_count': 0}
            
            if add_timestamp:
                if '$set' not in update_dict:
                    update_dict['$set'] = {}
                update_dict['$set']['updated_at'] = datetime.now()
            
            collection = self.get_collection(collection_name)
            result = collection.update_one(filter_dict, update_dict, upsert=upsert)
            
            update_info = {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None
            }
            
            logger.info(f"Updated document in {collection_name}: {update_info}")
            return update_info
            
        except Exception as e:
            logger.error(f"Error updating document in {collection_name}: {e}")
            raise

    def update_many(
        self,
        collection_name: str,
        filter_dict: Dict[str, Any],
        update_dict: Dict[str, Any],
        upsert: bool = False,
        add_timestamp: bool = True
    ) -> Dict[str, Any]:
        """
        Update multiple documents.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter
            update_dict: Update operations
            upsert: Whether to insert if no documents match
            add_timestamp: Whether to add updated_at timestamp
            
        Returns:
            Update result information
        """
        try:
            if add_timestamp:
                if '$set' not in update_dict:
                    update_dict['$set'] = {}
                update_dict['$set']['updated_at'] = datetime.now()
            
            collection = self.get_collection(collection_name)
            result = collection.update_many(filter_dict, update_dict, upsert=upsert)
            
            update_info = {
                'matched_count': result.matched_count,
                'modified_count': result.modified_count,
                'upserted_id': str(result.upserted_id) if result.upserted_id else None
            }
            
            logger.info(f"Updated {result.modified_count} documents in {collection_name}")
            return update_info
            
        except Exception as e:
            logger.error(f"Error updating documents in {collection_name}: {e}")
            raise

    def delete_one(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any]
    ) -> int:
        """
        Delete a single document.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter
            
        Returns:
            Number of deleted documents
        """
        try:
            # Convert string ID to ObjectId if needed
            if '_id' in filter_dict and isinstance(filter_dict['_id'], str):
                try:
                    filter_dict['_id'] = ObjectId(filter_dict['_id'])
                except InvalidId:
                    logger.warning(f"Invalid ObjectId format: {filter_dict['_id']}")
                    return 0
            
            collection = self.get_collection(collection_name)
            result = collection.delete_one(filter_dict)
            
            logger.info(f"Deleted {result.deleted_count} document from {collection_name}")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting document from {collection_name}: {e}")
            raise

    def delete_many(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any]
    ) -> int:
        """
        Delete multiple documents.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter
            
        Returns:
            Number of deleted documents
        """
        try:
            collection = self.get_collection(collection_name)
            result = collection.delete_many(filter_dict)
            
            logger.info(f"Deleted {result.deleted_count} documents from {collection_name}")
            return result.deleted_count
            
        except Exception as e:
            logger.error(f"Error deleting documents from {collection_name}: {e}")
            raise

    # ==================== Utility Methods ====================

    def count_documents(
        self, 
        collection_name: str, 
        filter_dict: Dict[str, Any] = None
    ) -> int:
        """
        Count documents in a collection.
        
        Args:
            collection_name: Name of the collection
            filter_dict: Query filter (empty dict for all documents)
            
        Returns:
            Number of documents
        """
        try:
            if filter_dict is None:
                filter_dict = {}
            
            collection = self.get_collection(collection_name)
            count = collection.count_documents(filter_dict)
            
            logger.info(f"Counted {count} documents in {collection_name}")
            return count
            
        except Exception as e:
            logger.error(f"Error counting documents in {collection_name}: {e}")
            raise

    def create_index(
        self, 
        collection_name: str, 
        keys: Union[str, List[tuple]], 
        **kwargs
    ) -> str:
        """
        Create an index on a collection.
        
        Args:
            collection_name: Name of the collection
            keys: Index specification
            **kwargs: Additional index options
            
        Returns:
            Index name
        """
        try:
            collection = self.get_collection(collection_name)
            index_name = collection.create_index(keys, **kwargs)
            
            logger.info(f"Created index '{index_name}' on {collection_name}")
            return index_name
            
        except Exception as e:
            logger.error(f"Error creating index on {collection_name}: {e}")
            raise

    def drop_index(self, collection_name: str, index_name: str) -> None:
        """
        Drop an index from a collection.
        
        Args:
            collection_name: Name of the collection
            index_name: Name of the index to drop
        """
        try:
            collection = self.get_collection(collection_name)
            collection.drop_index(index_name)
            
            logger.info(f"Dropped index '{index_name}' from {collection_name}")
            
        except Exception as e:
            logger.error(f"Error dropping index from {collection_name}: {e}")
            raise

    def list_indexes(self, collection_name: str) -> List[MutableMapping[str, Any]]:
        """
        List all indexes on a collection.
        
        Args:
            collection_name: Name of the collection
            
        Returns:
            List of index information
        """
        try:
            collection = self.get_collection(collection_name)
            indexes = list(collection.list_indexes())
            
            logger.info(f"Listed {len(indexes)} indexes for {collection_name}")
            return indexes
            
        except Exception as e:
            logger.error(f"Error listing indexes for {collection_name}: {e}")
            raise

    @asynccontextmanager
    async def transaction(self):
        """
        Context manager for MongoDB transactions.
        
        Usage:
            async with db_manager.transaction() as session:
                # Perform operations with session
                pass
        """
        session = self.client.start_session()
        try:
            async with session.start_transaction():
                yield session
        except Exception as e:
            logger.error(f"Transaction failed: {e}")
            raise
        finally:
            session.end_session()

    def aggregate(
        self, 
        collection_name: str, 
        pipeline: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Perform aggregation on a collection.
        
        Args:
            collection_name: Name of the collection
            pipeline: Aggregation pipeline
            
        Returns:
            Aggregation results
        """
        try:
            collection = self.get_collection(collection_name)
            results = list(collection.aggregate(pipeline))
            
            # Convert ObjectId to string in results
            for doc in results:
                if '_id' in doc and isinstance(doc['_id'], ObjectId):
                    doc['_id'] = str(doc['_id'])
            
            logger.info(f"Aggregation on {collection_name} returned {len(results)} results")
            return results
            
        except Exception as e:
            logger.error(f"Error in aggregation on {collection_name}: {e}")
            raise

    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the MongoDB connection.
        
        Returns:
            Health check results
        """
        try:
            # Test basic connectivity
            self.client.admin.command('ping')
            
            # Get server info
            server_info = self.client.server_info()
            
            # Get database stats
            db_stats = self.database.command('dbStats')
            
            health_info = {
                'status': 'healthy',
                'server_version': server_info.get('version'),
                'database_name': self.database_name,
                'collections_count': len(self.database.list_collection_names()),
                'database_size_mb': round(db_stats.get('dataSize', 0) / (1024 * 1024), 2)
            }
            
            logger.info("MongoDB health check passed")
            return health_info
            
        except Exception as e:
            logger.error(f"MongoDB health check failed: {e}")
            return {
                'status': 'unhealthy',
                'error': str(e)
            }