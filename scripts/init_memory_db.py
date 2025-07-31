#!/usr/bin/env python3
"""Initialize SQLite database for memory MCP server."""

import sqlite3
import os
from pathlib import Path

def init_memory_db():
    """Create and initialize the memory.db SQLite database."""
    # Get the current directory
    current_dir = Path(__file__).parent
    db_path = current_dir / "memory.db"

    # Create or connect to the database
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # Create tables for memory storage
    # This is a basic schema - adjust based on your memory MCP server requirements
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create an index on the key column for faster lookups
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_memories_key ON memories(key)
    """)

    # Create a metadata table
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS metadata (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            version TEXT NOT NULL,
            initialized_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Insert initial metadata
    cursor.execute("""
        INSERT OR IGNORE INTO metadata (id, version) VALUES (1, '1.0.0')
    """)

    # Commit the changes
    conn.commit()
    conn.close()

    print(f"Memory database initialized at: {db_path}")
    print(f"Database size: {os.path.getsize(db_path)} bytes")

if __name__ == "__main__":
    init_memory_db()
