#!/usr/bin/env python3
"""
Created: 2025-08-09T15:35:00-06:00
Check record counts in both DEV and PRD databases
"""
import asyncio
from surrealdb import AsyncSurreal
from datetime import datetime

async def check_database(url: str, namespace: str, database: str, env_name: str):
    """Check record counts in a database."""
    print(f"\n{'='*60}")
    print(f"{env_name} DATABASE CHECK")
    print(f"URL: {url}")
    print(f"Namespace: {namespace}")
    print(f"Database: {database}")
    print(f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"{'='*60}\n")
    
    db = AsyncSurreal(url)
    
    try:
        # Connect
        await db.connect()
        await db.signin({"username": "root", "password": "root"})
        await db.use(namespace, database)
        
        # Get database info
        info_result = await db.query("INFO FOR DB")
        if info_result:
            tables = info_result.get('tables', {})
            print(f"Tables found: {', '.join(tables.keys()) if tables else 'NONE'}\n")
        
        # Check each table
        table_counts = {}
        tables_to_check = [
            'user', 'patient', 'alert', 'audit_log', 'audit_logs',
            'chat_history', 'metrics', 'system_alerts', 'rate_limit_entry'
        ]
        
        print("TABLE RECORD COUNTS:")
        print("-" * 40)
        print(f"{'Table':<20} {'Count':<10}")
        print("-" * 40)
        
        total_records = 0
        for table in tables_to_check:
            try:
                result = await db.query(f"SELECT count() FROM {table} GROUP ALL")
                if result and len(result) > 0:
                    count = result[0].get('count', 0)
                    table_counts[table] = count
                    total_records += count
                    print(f"{table:<20} {count:<10}")
                else:
                    print(f"{table:<20} {'0':<10}")
            except Exception as e:
                print(f"{table:<20} {'N/A':<10} (table may not exist)")
        
        print("-" * 40)
        print(f"{'TOTAL RECORDS':<20} {total_records:<10}")
        
        return table_counts
        
    except Exception as e:
        print(f"ERROR: Unable to connect to {env_name} database")
        print(f"Error details: {e}")
        return {}
    finally:
        try:
            await db.close()
        except:
            pass

async def main():
    """Check both DEV and PRD databases."""
    print("\nDATABASE RECORD COUNT CHECK")
    print("="*60)
    
    # Check DEV
    dev_counts = await check_database(
        "ws://localhost:8000/rpc",
        "patient_dashboard_dev",
        "patient_dashboard_dev",
        "DEV"
    )
    
    # Check PRD
    prd_counts = await check_database(
        "ws://localhost:8080/rpc",
        "patient_dashboard",
        "patient_dashboard",
        "PRD"
    )
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    if dev_counts:
        print(f"DEV Database: Connected successfully")
        print(f"  - Total tables with data: {sum(1 for v in dev_counts.values() if v > 0)}")
        print(f"  - Total records: {sum(dev_counts.values())}")
    else:
        print(f"DEV Database: NOT CONNECTED")
    
    if prd_counts:
        print(f"\nPRD Database: Connected successfully")
        print(f"  - Total tables with data: {sum(1 for v in prd_counts.values() if v > 0)}")
        print(f"  - Total records: {sum(prd_counts.values())}")
    else:
        print(f"\nPRD Database: NOT CONNECTED")
    
    print("\nNote: Databases must be started first using ./scripts/start_dual_databases.sh")

if __name__ == "__main__":
    asyncio.run(main())