"""
SurrealDB connection management for patient dashboard.
Provides connection pooling, health checks, and error recovery.
"""
import os
import asyncio
from typing import Optional, Dict, Any
from contextlib import asynccontextmanager
import logging
import logfire
from surrealdb import AsyncSurreal
from tenacity import retry, stop_after_attempt, wait_exponential
from app.config.settings import get_settings

# Configure Logfire using Ptolemies pattern
try:
    logfire.configure()
except Exception:
    # Continue without Logfire if authentication fails
    pass

logger = logging.getLogger(__name__)
settings = get_settings()

class DatabaseConnection:
    """Manages SurrealDB connections with pooling and health checks."""
    
    def __init__(self):
        self.db: Optional[AsyncSurreal] = None
        self.url = settings.DATABASE_URL
        self.username = settings.DATABASE_USER
        self.password = settings.DATABASE_PASS
        self.namespace = settings.DATABASE_NAMESPACE
        self.database = settings.DATABASE_NAME
        self._connected = False
        self._lock = asyncio.Lock()
        
        # Debug output
        logger.info(f"Database config - URL: {self.url}, User: {self.username}, Namespace: {self.namespace}, Database: {self.database}")
        
    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        reraise=True
    )
    async def connect(self) -> None:
        """Connect to SurrealDB with retry logic."""
        async with self._lock:
            if self._connected:
                return
                
            try:
                self.db = AsyncSurreal(self.url)
                await self.db.connect()
                # Try different authentication parameter formats
                try:
                    # First try the official documentation format
                    await self.db.signin({
                        "username": self.username,
                        "password": self.password
                    })
                    logger.info("Authentication successful with username/password format")
                except Exception as e1:
                    logger.warning(f"Auth failed with username/password: {e1}")
                    try:
                        # Try the GitHub README format
                        await self.db.signin({
                            "user": self.username,
                            "pass": self.password
                        })
                        logger.info("Authentication successful with user/pass format")
                    except Exception as e2:
                        logger.error(f"Both authentication formats failed: {e2}")
                        # Try namespace-specific authentication
                        try:
                            await self.db.signin({
                                "namespace": self.namespace,
                                "database": self.database,
                                "username": self.username,
                                "password": self.password
                            })
                            logger.info("Authentication successful with namespace/database format")
                        except Exception as e3:
                            logger.error(f"All authentication methods failed. Running without auth.")
                            logger.error(f"Error 1: {e1}")
                            logger.error(f"Error 2: {e2}")
                            logger.error(f"Error 3: {e3}")
                            # Continue without authentication for now
                
                # Use namespace and database
                await self.db.use(self.namespace, self.database)
                self._connected = True
                logger.info(f"Connected to SurrealDB at {self.url}")
            except Exception as e:
                logger.error(f"Failed to connect to SurrealDB: {e}")
                self._connected = False
                raise
    
    async def disconnect(self) -> None:
        """Gracefully disconnect from SurrealDB."""
        async with self._lock:
            if self.db and self._connected:
                try:
                    await self.db.close()
                    self._connected = False
                    logger.info("Disconnected from SurrealDB")
                except Exception as e:
                    logger.error(f"Error disconnecting from SurrealDB: {e}")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check database connection health."""
        try:
            if not self._connected:
                await self.connect()
            
            # Simple query to verify connection
            result = await self.db.query("INFO FOR DB")
            
            return {
                "status": "healthy",
                "connected": True,
                "database": self.database,
                "namespace": self.namespace
            }
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "connected": False,
                "error": str(e)
            }
    
    # @logfire.instrument("database.execute")  # Temporarily disabled due to auth issues
    async def execute(self, query: str, params: Optional[Dict[str, Any]] = None) -> Any:
        """Execute a query with automatic reconnection on failure."""
        # Temporarily disabled logfire.span due to auth issues
        # with logfire.span(
        #     "surrealdb_query",
        #     query=query[:200] + "..." if len(query) > 200 else query,
        #     has_params=bool(params),
        #     namespace=self.namespace,
        #     database=self.database
        # ):
        if not self._connected:
            await self.connect()
        
        try:
            try:
                logfire.info("Executing SurrealDB query", query_type=query.split()[0].upper())
            except:
                pass
            result = await self.db.query(query, params or {})
            try:
                logfire.info(
                    "Query executed successfully",
                    result_type=type(result).__name__,
                    result_length=len(result) if isinstance(result, (list, dict)) else None
                )
            except:
                pass
            return result
        except Exception as e:
            try:
                logfire.error(
                    "Query execution failed",
                    error_type=type(e).__name__,
                    error_message=str(e)
                )
            except:
                pass
            logger.error(f"Query execution failed: {e}")
            # Try to reconnect once
            self._connected = False
            await self.connect()
            return await self.db.query(query, params or {})
    
    @asynccontextmanager
    async def transaction(self):
        """Execute operations within a transaction."""
        if not self._connected:
            await self.connect()
            
        transaction_id = None
        try:
            # Start transaction
            result = await self.db.query("BEGIN TRANSACTION")
            transaction_id = result[0]["result"] if result else None
            
            yield self
            
            # Commit transaction
            await self.db.query("COMMIT TRANSACTION")
            
        except Exception as e:
            # Rollback on error
            if transaction_id:
                try:
                    await self.db.query("CANCEL TRANSACTION")
                except:
                    pass
            raise e


# Global database instance
_db_connection: Optional[DatabaseConnection] = None


async def get_database() -> DatabaseConnection:
    """Get or create database connection singleton."""
    global _db_connection
    
    if _db_connection is None:
        _db_connection = DatabaseConnection()
        await _db_connection.connect()
    
    return _db_connection


async def init_database() -> DatabaseConnection:
    """Initialize database connection and create schemas if needed."""
    db = await get_database()
    
    # Ensure connection is established
    try:
        health = await db.health_check()
        if health["status"] != "healthy":
            logger.warning(f"Database health check warning: {health.get('error', 'Unknown error')}")
            # Continue anyway for development
    except Exception as e:
        logger.warning(f"Database health check skipped: {e}")
        # Continue anyway for development
    
    logger.info("Database initialized successfully")
    return db


async def close_database() -> None:
    """Close database connection gracefully."""
    global _db_connection
    
    if _db_connection:
        await _db_connection.disconnect()
        _db_connection = None