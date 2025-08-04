-- PFINNI Patient Dashboard Database Schema
-- SurrealDB schema definitions for MVP
-- Generated: 2025-01-28

-- Enable strict mode for data validation
DEFINE NAMESPACE patient_dashboard;
DEFINE DATABASE patient_dashboard;

-- ============================================
-- USERS TABLE
-- ============================================
DEFINE TABLE user SCHEMAFULL;

DEFINE FIELD email ON TABLE user TYPE string ASSERT string::is::email($value);
DEFINE FIELD password_hash ON TABLE user TYPE string;
DEFINE FIELD first_name ON TABLE user TYPE string;
DEFINE FIELD last_name ON TABLE user TYPE string;
DEFINE FIELD role ON TABLE user TYPE string ASSERT $value IN ['PROVIDER', 'ADMIN', 'AUDIT'];
DEFINE FIELD is_active ON TABLE user TYPE bool DEFAULT true;
DEFINE FIELD created_at ON TABLE user TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON TABLE user TYPE datetime DEFAULT time::now();
DEFINE FIELD last_login ON TABLE user TYPE option<datetime>;

DEFINE INDEX user_email_unique ON TABLE user COLUMNS email UNIQUE;
DEFINE INDEX user_role_idx ON TABLE user COLUMNS role;
DEFINE INDEX user_active_idx ON TABLE user COLUMNS is_active;

-- ============================================
-- PATIENTS TABLE
-- ============================================
DEFINE TABLE patient SCHEMAFULL;

DEFINE FIELD medical_record_number ON TABLE patient TYPE string;
DEFINE FIELD first_name ON TABLE patient TYPE string;
DEFINE FIELD last_name ON TABLE patient TYPE string;
DEFINE FIELD date_of_birth ON TABLE patient TYPE datetime;
DEFINE FIELD gender ON TABLE patient TYPE string ASSERT $value IN ['MALE', 'FEMALE', 'OTHER'];
DEFINE FIELD email ON TABLE patient TYPE option<string> ASSERT $value = NONE OR string::is::email($value);
DEFINE FIELD phone ON TABLE patient TYPE option<string>;
DEFINE FIELD address_line1 ON TABLE patient TYPE option<string>;
DEFINE FIELD address_line2 ON TABLE patient TYPE option<string>;
DEFINE FIELD city ON TABLE patient TYPE option<string>;
DEFINE FIELD state ON TABLE patient TYPE option<string>;
DEFINE FIELD postal_code ON TABLE patient TYPE option<string>;
DEFINE FIELD status ON TABLE patient TYPE string DEFAULT 'INQUIRY' ASSERT $value IN ['INQUIRY', 'ONBOARDING', 'ACTIVE', 'CHURNED'];
DEFINE FIELD status_changed_at ON TABLE patient TYPE datetime DEFAULT time::now();
DEFINE FIELD status_changed_by ON TABLE patient TYPE option<record<user>>;
DEFINE FIELD assigned_provider ON TABLE patient TYPE option<record<user>>;
DEFINE FIELD insurance_member_id ON TABLE patient TYPE option<string>;
DEFINE FIELD insurance_status ON TABLE patient TYPE option<string>;
DEFINE FIELD created_at ON TABLE patient TYPE datetime DEFAULT time::now();
DEFINE FIELD updated_at ON TABLE patient TYPE datetime DEFAULT time::now();
DEFINE FIELD created_by ON TABLE patient TYPE record<user>;
DEFINE FIELD is_deleted ON TABLE patient TYPE bool DEFAULT false;

DEFINE INDEX patient_mrn_unique ON TABLE patient COLUMNS medical_record_number UNIQUE;
DEFINE INDEX patient_status_idx ON TABLE patient COLUMNS status;
DEFINE INDEX patient_name_idx ON TABLE patient COLUMNS first_name, last_name;
DEFINE INDEX patient_dob_idx ON TABLE patient COLUMNS date_of_birth;
DEFINE INDEX patient_provider_idx ON TABLE patient COLUMNS assigned_provider;
DEFINE INDEX patient_deleted_idx ON TABLE patient COLUMNS is_deleted;

-- ============================================
-- ALERTS TABLE
-- ============================================
DEFINE TABLE alert SCHEMAFULL;

DEFINE FIELD type ON TABLE alert TYPE string ASSERT $value IN ['BIRTHDAY', 'STATUS_CHANGE', 'INSURANCE_EXPIRY', 'SYSTEM', 'URGENT'];
DEFINE FIELD priority ON TABLE alert TYPE string DEFAULT 'MEDIUM' ASSERT $value IN ['LOW', 'MEDIUM', 'HIGH', 'URGENT'];
DEFINE FIELD title ON TABLE alert TYPE string;
DEFINE FIELD message ON TABLE alert TYPE string;
DEFINE FIELD patient_id ON TABLE alert TYPE option<record<patient>>;
DEFINE FIELD user_id ON TABLE alert TYPE record<user>;
DEFINE FIELD is_read ON TABLE alert TYPE bool DEFAULT false;
DEFINE FIELD read_at ON TABLE alert TYPE option<datetime>;
DEFINE FIELD is_acknowledged ON TABLE alert TYPE bool DEFAULT false;
DEFINE FIELD acknowledged_at ON TABLE alert TYPE option<datetime>;
DEFINE FIELD acknowledged_by ON TABLE alert TYPE option<record<user>>;
DEFINE FIELD created_at ON TABLE alert TYPE datetime DEFAULT time::now();
DEFINE FIELD expires_at ON TABLE alert TYPE option<datetime>;

DEFINE INDEX alert_user_idx ON TABLE alert COLUMNS user_id;
DEFINE INDEX alert_patient_idx ON TABLE alert COLUMNS patient_id;
DEFINE INDEX alert_type_idx ON TABLE alert COLUMNS type;
DEFINE INDEX alert_priority_idx ON TABLE alert COLUMNS priority;
DEFINE INDEX alert_read_idx ON TABLE alert COLUMNS is_read;
DEFINE INDEX alert_created_idx ON TABLE alert COLUMNS created_at;

-- ============================================
-- AUDIT_LOG TABLE
-- ============================================
DEFINE TABLE audit_log SCHEMAFULL;

DEFINE FIELD action ON TABLE audit_log TYPE string ASSERT $value IN ['CREATE', 'READ', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'STATUS_CHANGE'];
DEFINE FIELD resource_type ON TABLE audit_log TYPE string ASSERT $value IN ['PATIENT', 'USER', 'ALERT', 'REPORT', 'SYSTEM'];
DEFINE FIELD resource_id ON TABLE audit_log TYPE option<string>;
DEFINE FIELD user_id ON TABLE audit_log TYPE record<user>;
DEFINE FIELD user_email ON TABLE audit_log TYPE string;
DEFINE FIELD user_role ON TABLE audit_log TYPE string;
DEFINE FIELD ip_address ON TABLE audit_log TYPE option<string>;
DEFINE FIELD user_agent ON TABLE audit_log TYPE option<string>;
DEFINE FIELD request_id ON TABLE audit_log TYPE option<string>;
DEFINE FIELD changes ON TABLE audit_log TYPE option<object>;
DEFINE FIELD success ON TABLE audit_log TYPE bool DEFAULT true;
DEFINE FIELD error_message ON TABLE audit_log TYPE option<string>;
DEFINE FIELD created_at ON TABLE audit_log TYPE datetime DEFAULT time::now();

-- Audit logs should never be deleted, only indexes for querying
DEFINE INDEX audit_user_idx ON TABLE audit_log COLUMNS user_id;
DEFINE INDEX audit_action_idx ON TABLE audit_log COLUMNS action;
DEFINE INDEX audit_resource_idx ON TABLE audit_log COLUMNS resource_type, resource_id;
DEFINE INDEX audit_created_idx ON TABLE audit_log COLUMNS created_at;
DEFINE INDEX audit_success_idx ON TABLE audit_log COLUMNS success;

-- ============================================
-- CHAT_HISTORY TABLE (for AI Assistant)
-- ============================================
DEFINE TABLE chat_history SCHEMAFULL;

DEFINE FIELD user_id ON TABLE chat_history TYPE record<user>;
DEFINE FIELD session_id ON TABLE chat_history TYPE string;
DEFINE FIELD message_type ON TABLE chat_history TYPE string ASSERT $value IN ['USER', 'ASSISTANT', 'SYSTEM'];
DEFINE FIELD message ON TABLE chat_history TYPE string;
DEFINE FIELD context ON TABLE chat_history TYPE option<object>;
DEFINE FIELD created_at ON TABLE chat_history TYPE datetime DEFAULT time::now();

DEFINE INDEX chat_user_idx ON TABLE chat_history COLUMNS user_id;
DEFINE INDEX chat_session_idx ON TABLE chat_history COLUMNS session_id;
DEFINE INDEX chat_created_idx ON TABLE chat_history COLUMNS created_at;

-- ============================================
-- HELPER FUNCTIONS
-- ============================================

-- Function to update timestamps
DEFINE FUNCTION fn::update_timestamp() {
    UPDATE $this SET updated_at = time::now();
};

-- Function to log status changes
DEFINE FUNCTION fn::log_status_change($patient_id: record<patient>, $old_status: string, $new_status: string, $user_id: record<user>) {
    CREATE audit_log SET
        action = 'STATUS_CHANGE',
        resource_type = 'PATIENT',
        resource_id = $patient_id,
        user_id = $user_id,
        changes = {
            old_status: $old_status,
            new_status: $new_status
        },
        created_at = time::now();
};

-- ============================================
-- EVENTS (Triggers)
-- ============================================

-- Auto-update timestamp on patient changes
DEFINE EVENT patient_updated ON TABLE patient WHEN $event = "UPDATE" THEN (
    UPDATE $this SET updated_at = time::now()
);

-- Log patient status changes
DEFINE EVENT patient_status_changed ON TABLE patient WHEN $event = "UPDATE" AND $before.status != $after.status THEN (
    fn::log_status_change($this.id, $before.status, $after.status, $after.status_changed_by)
);

-- ============================================
-- RATE LIMITING
-- ============================================

-- Rate limit entries table
DEFINE TABLE rate_limit_entry SCHEMALESS;

-- Indexes for efficient rate limit queries
DEFINE INDEX rate_limit_bucket_idx ON TABLE rate_limit_entry COLUMNS bucket;
DEFINE INDEX rate_limit_timestamp_idx ON TABLE rate_limit_entry COLUMNS timestamp;
DEFINE INDEX rate_limit_composite_idx ON TABLE rate_limit_entry COLUMNS bucket, timestamp;