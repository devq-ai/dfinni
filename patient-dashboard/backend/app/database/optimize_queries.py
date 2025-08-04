"""
Database query optimization with indexes for SurrealDB.
Per Production Proposal Phase 2: Optimize database queries with indexes
"""
import asyncio
import logfire
from typing import List, Dict, Any

from app.database.connection import DatabaseConnection
from app.config.settings import get_settings

settings = get_settings()


class DatabaseOptimizer:
    """Service for optimizing database queries with proper indexes."""
    
    def __init__(self):
        self.db: DatabaseConnection = None
        self.indexes_created = []
    
    async def connect(self):
        """Connect to database."""
        if not self.db:
            self.db = DatabaseConnection()
            await self.db.connect()
    
    async def create_indexes(self) -> List[Dict[str, Any]]:
        """Create all necessary indexes for optimal query performance."""
        indexes = []
        
        # User table indexes
        user_indexes = [
            ("user_email_idx", "user", ["email"], True),  # Unique index
            ("user_clerk_id_idx", "user", ["clerk_user_id"], True),  # Unique index
            ("user_role_idx", "user", ["role"], False),
            ("user_active_idx", "user", ["is_active"], False),
            ("user_created_idx", "user", ["created_at"], False),
        ]
        
        # Patient table indexes
        patient_indexes = [
            ("patient_mrn_idx", "patient", ["medical_record_number"], True),  # Unique index
            ("patient_status_idx", "patient", ["status"], False),
            ("patient_created_by_idx", "patient", ["created_by"], False),
            ("patient_created_idx", "patient", ["created_at"], False),
            ("patient_name_idx", "patient", ["last_name", "first_name"], False),
            ("patient_ssn_idx", "patient", ["ssn"], True),  # Unique index for SSN
            ("patient_email_idx", "patient", ["email"], False),
            ("patient_phone_idx", "patient", ["phone"], False),
        ]
        
        # Alert table indexes
        alert_indexes = [
            ("alert_patient_idx", "alert", ["patient_id"], False),
            ("alert_severity_idx", "alert", ["severity"], False),
            ("alert_status_idx", "alert", ["status"], False),
            ("alert_created_idx", "alert", ["created_at"], False),
            ("alert_type_idx", "alert", ["type"], False),
            ("alert_assigned_idx", "alert", ["assigned_to"], False),
        ]
        
        # Appointment table indexes
        appointment_indexes = [
            ("appointment_patient_idx", "appointment", ["patient_id"], False),
            ("appointment_provider_idx", "appointment", ["provider_id"], False),
            ("appointment_date_idx", "appointment", ["appointment_date"], False),
            ("appointment_status_idx", "appointment", ["status"], False),
            ("appointment_type_idx", "appointment", ["type"], False),
        ]
        
        # Medication table indexes
        medication_indexes = [
            ("medication_patient_idx", "medication", ["patient_id"], False),
            ("medication_active_idx", "medication", ["is_active"], False),
            ("medication_name_idx", "medication", ["name"], False),
            ("medication_prescribed_idx", "medication", ["prescribed_date"], False),
        ]
        
        # Audit log indexes
        audit_indexes = [
            ("audit_user_idx", "audit_logs", ["user_id"], False),
            ("audit_timestamp_idx", "audit_logs", ["timestamp"], False),
            ("audit_resource_idx", "audit_logs", ["resource", "resource_id"], False),
            ("audit_patient_idx", "audit_logs", ["patient_id"], False),
            ("audit_action_idx", "audit_logs", ["action"], False),
            ("audit_success_idx", "audit_logs", ["success"], False),
        ]
        
        # Analytics table indexes
        analytics_indexes = [
            ("analytics_metric_idx", "analytics_metrics", ["metric_name"], False),
            ("analytics_timestamp_idx", "analytics_metrics", ["timestamp"], False),
            ("analytics_user_idx", "analytics_metrics", ["user_id"], False),
            ("analytics_patient_idx", "analytics_metrics", ["patient_id"], False),
        ]
        
        # Combine all indexes
        all_indexes = (
            user_indexes + patient_indexes + alert_indexes +
            appointment_indexes + medication_indexes + audit_indexes +
            analytics_indexes
        )
        
        # Create each index
        for index_name, table, columns, is_unique in all_indexes:
            try:
                result = await self._create_index(
                    index_name, table, columns, is_unique
                )
                indexes.append(result)
                logfire.info(
                    f"Created index {index_name}",
                    table=table,
                    columns=columns,
                    unique=is_unique
                )
            except Exception as e:
                logfire.error(
                    f"Failed to create index {index_name}",
                    error=str(e),
                    table=table,
                    columns=columns
                )
                indexes.append({
                    "name": index_name,
                    "table": table,
                    "columns": columns,
                    "unique": is_unique,
                    "status": "failed",
                    "error": str(e)
                })
        
        self.indexes_created = indexes
        return indexes
    
    async def _create_index(
        self,
        index_name: str,
        table: str,
        columns: List[str],
        is_unique: bool = False
    ) -> Dict[str, Any]:
        """Create a single index."""
        columns_str = ", ".join(columns)
        unique_str = "UNIQUE " if is_unique else ""
        
        query = f"DEFINE INDEX {index_name} ON TABLE {table} COLUMNS {columns_str} {unique_str}"
        
        await self.db.query(query.strip())
        
        return {
            "name": index_name,
            "table": table,
            "columns": columns,
            "unique": is_unique,
            "status": "created"
        }
    
    async def create_full_text_search_indexes(self) -> List[Dict[str, Any]]:
        """Create full-text search indexes for searchable fields."""
        fts_indexes = []
        
        # Patient search index
        try:
            query = """
            DEFINE INDEX patient_search_idx ON TABLE patient 
            COLUMNS first_name, last_name, medical_record_number, email
            SEARCH ANALYZER ascii FILTERS lowercase, edgengram(2,20)
            """
            await self.db.query(query)
            
            fts_indexes.append({
                "name": "patient_search_idx",
                "table": "patient",
                "type": "full_text_search",
                "status": "created"
            })
            
            logfire.info("Created full-text search index for patients")
        except Exception as e:
            logfire.error("Failed to create patient FTS index", error=str(e))
            fts_indexes.append({
                "name": "patient_search_idx",
                "table": "patient",
                "type": "full_text_search",
                "status": "failed",
                "error": str(e)
            })
        
        return fts_indexes
    
    async def analyze_query_performance(self) -> Dict[str, Any]:
        """Analyze common queries and their performance."""
        queries_to_analyze = [
            # Patient queries
            ("patient_list", "SELECT * FROM patient WHERE status = 'active' ORDER BY created_at DESC LIMIT 20"),
            ("patient_search", "SELECT * FROM patient WHERE first_name ~= 'john' OR last_name ~= 'john' LIMIT 10"),
            ("patient_by_mrn", "SELECT * FROM patient WHERE medical_record_number = 'MRN123456'"),
            
            # Alert queries
            ("active_alerts", "SELECT * FROM alert WHERE status = 'active' AND severity IN ['critical', 'high'] ORDER BY created_at DESC"),
            ("patient_alerts", "SELECT * FROM alert WHERE patient_id = 'patient:123' ORDER BY created_at DESC LIMIT 10"),
            
            # Dashboard queries
            ("patient_stats", "SELECT count() as total, status FROM patient GROUP BY status"),
            ("recent_activity", """
                SELECT * FROM (
                    SELECT 'patient' as type, id, created_at FROM patient
                    UNION
                    SELECT 'alert' as type, id, created_at FROM alert
                    UNION
                    SELECT 'appointment' as type, id, created_at FROM appointment
                ) ORDER BY created_at DESC LIMIT 20
            """),
            
            # Audit queries
            ("user_audit", "SELECT * FROM audit_logs WHERE user_id = 'user:123' ORDER BY timestamp DESC LIMIT 50"),
            ("patient_access_audit", "SELECT * FROM audit_logs WHERE patient_id = 'patient:123' AND phi_accessed = true ORDER BY timestamp DESC"),
        ]
        
        analysis_results = []
        
        for query_name, query in queries_to_analyze:
            try:
                # Use EXPLAIN to analyze query plan
                explain_query = f"EXPLAIN {query}"
                result = await self.db.query(explain_query)
                
                analysis_results.append({
                    "name": query_name,
                    "query": query,
                    "plan": result,
                    "status": "analyzed"
                })
                
                logfire.info(f"Analyzed query: {query_name}")
            except Exception as e:
                analysis_results.append({
                    "name": query_name,
                    "query": query,
                    "status": "failed",
                    "error": str(e)
                })
                logfire.error(f"Failed to analyze query: {query_name}", error=str(e))
        
        return {
            "queries_analyzed": len(analysis_results),
            "results": analysis_results
        }
    
    async def create_materialized_views(self) -> List[Dict[str, Any]]:
        """Create materialized views for complex dashboard queries."""
        views = []
        
        # Patient statistics view
        try:
            query = """
            DEFINE TABLE patient_stats_view AS
            SELECT 
                count() as total,
                count(status = 'active') as active,
                count(status = 'inactive') as inactive,
                count(status = 'inquiry') as inquiry,
                count(status = 'onboarding') as onboarding,
                count(status = 'churned') as churned,
                count(status = 'urgent') as urgent,
                time::now() as last_updated
            FROM patient
            """
            await self.db.query(query)
            
            views.append({
                "name": "patient_stats_view",
                "type": "statistics",
                "status": "created"
            })
            
            logfire.info("Created patient statistics view")
        except Exception as e:
            logfire.error("Failed to create patient stats view", error=str(e))
            views.append({
                "name": "patient_stats_view",
                "type": "statistics",
                "status": "failed",
                "error": str(e)
            })
        
        # Alert summary view
        try:
            query = """
            DEFINE TABLE alert_summary_view AS
            SELECT 
                count() as total,
                count(severity = 'critical') as critical,
                count(severity = 'high') as high,
                count(severity = 'medium') as medium,
                count(severity = 'low') as low,
                count(status = 'active') as active,
                count(status = 'resolved') as resolved,
                time::now() as last_updated
            FROM alert
            WHERE created_at > time::now() - 7d
            """
            await self.db.query(query)
            
            views.append({
                "name": "alert_summary_view",
                "type": "alert_summary",
                "status": "created"
            })
            
            logfire.info("Created alert summary view")
        except Exception as e:
            logfire.error("Failed to create alert summary view", error=str(e))
            views.append({
                "name": "alert_summary_view",
                "type": "alert_summary",
                "status": "failed",
                "error": str(e)
            })
        
        return views
    
    async def optimize_all(self) -> Dict[str, Any]:
        """Run all optimization tasks."""
        with logfire.span("database_optimization"):
            await self.connect()
            
            # Create standard indexes
            logfire.info("Creating database indexes")
            indexes = await self.create_indexes()
            
            # Create full-text search indexes
            logfire.info("Creating full-text search indexes")
            fts_indexes = await self.create_full_text_search_indexes()
            
            # Create materialized views
            logfire.info("Creating materialized views")
            views = await self.create_materialized_views()
            
            # Analyze query performance
            logfire.info("Analyzing query performance")
            analysis = await self.analyze_query_performance()
            
            return {
                "indexes_created": len([i for i in indexes if i.get("status") == "created"]),
                "indexes_failed": len([i for i in indexes if i.get("status") == "failed"]),
                "fts_indexes": fts_indexes,
                "materialized_views": views,
                "query_analysis": analysis,
                "total_optimizations": len(indexes) + len(fts_indexes) + len(views)
            }


async def run_optimization():
    """Run database optimization."""
    optimizer = DatabaseOptimizer()
    
    try:
        logfire.info("Starting database optimization")
        results = await optimizer.optimize_all()
        
        logfire.info(
            "Database optimization completed",
            indexes_created=results["indexes_created"],
            indexes_failed=results["indexes_failed"],
            total_optimizations=results["total_optimizations"]
        )
        
        return results
    except Exception as e:
        logfire.error("Database optimization failed", error=str(e))
        raise


if __name__ == "__main__":
    # Run optimization when executed directly
    asyncio.run(run_optimization())