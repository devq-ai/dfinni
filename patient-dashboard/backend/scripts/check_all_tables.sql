-- Created: 2025-08-09T15:35:00-06:00
-- SQL script to check record counts in all tables

-- Check if tables exist and count records
INFO FOR DB;

-- Count records in each table
SELECT 'user' as table_name, count() as record_count FROM user GROUP ALL;
SELECT 'patient' as table_name, count() as record_count FROM patient GROUP ALL;
SELECT 'alert' as table_name, count() as record_count FROM alert GROUP ALL;
SELECT 'audit_log' as table_name, count() as record_count FROM audit_log GROUP ALL;
SELECT 'audit_logs' as table_name, count() as record_count FROM audit_logs GROUP ALL;
SELECT 'chat_history' as table_name, count() as record_count FROM chat_history GROUP ALL;
SELECT 'metrics' as table_name, count() as record_count FROM metrics GROUP ALL;
SELECT 'system_alerts' as table_name, count() as record_count FROM system_alerts GROUP ALL;
SELECT 'rate_limit_entry' as table_name, count() as record_count FROM rate_limit_entry GROUP ALL;

-- Show total summary
SELECT 'TOTAL_TABLES' as metric, count() as value FROM (SELECT meta::tb as tbl FROM user, patient, alert, audit_log, chat_history GROUP ALL) GROUP ALL;