<!-- Updated: 2025-07-27T12:58:15-05:00 -->
patient-dashboard/
├── README.md
├── .gitignore
├── .env.example
├── docker-compose.yml
├── Dockerfile
├── pyproject.toml
├── requirements.txt
├── .github/
│   └── workflows/
│       ├── ci.yml
│       ├── cd.yml
│       └── security-scan.yml
├── docs/
│   ├── api/
│   │   ├── endpoints.md
│   │   ├── authentication.md
│   │   └── schemas.md
│   ├── deployment/
│   │   ├── production.md
│   │   ├── staging.md
│   │   └── local-development.md
│   ├── architecture/
│   │   ├── system-design.md
│   │   ├── database-schema.md
│   │   └── security.md
│   └── user-guides/
│       ├── provider-guide.md
│       └── admin-guide.md
├── backend/
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── config/
│   │   │   ├── __init__.py
│   │   │   ├── settings.py
│   │   │   ├── database.py
│   │   │   ├── auth.py
│   │   │   ├── logging.py
│   │   │   └── monitoring.py
│   │   ├── core/
│   │   │   ├── __init__.py
│   │   │   ├── security.py
│   │   │   ├── auth.py
│   │   │   ├── middleware.py
│   │   │   ├── exceptions.py
│   │   │   ├── dependencies.py
│   │   │   └── utils.py
│   │   ├── models/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── patient.py
│   │   │   ├── user.py
│   │   │   ├── audit.py
│   │   │   ├── insurance.py
│   │   │   └── alert.py
│   │   ├── schemas/
│   │   │   ├── __init__.py
│   │   │   ├── patient.py
│   │   │   ├── user.py
│   │   │   ├── auth.py
│   │   │   ├── insurance.py
│   │   │   ├── alert.py
│   │   │   └── common.py
│   │   ├── api/
│   │   │   ├── __init__.py
│   │   │   ├── deps.py
│   │   │   └── v1/
│   │   │       ├── __init__.py
│   │   │       ├── auth.py
│   │   │       ├── patients.py
│   │   │       ├── users.py
│   │   │       ├── dashboard.py
│   │   │       ├── alerts.py
│   │   │       ├── insurance.py
│   │   │       ├── reports.py
│   │   │       └── webhooks.py
│   │   ├── services/
│   │   │   ├── __init__.py
│   │   │   ├── patient_service.py
│   │   │   ├── user_service.py
│   │   │   ├── auth_service.py
│   │   │   ├── insurance_service.py
│   │   │   ├── alert_service.py
│   │   │   ├── notification_service.py
│   │   │   ├── audit_service.py
│   │   │   └── data_quality_service.py
│   │   ├── repositories/
│   │   │   ├── __init__.py
│   │   │   ├── base.py
│   │   │   ├── patient_repository.py
│   │   │   ├── user_repository.py
│   │   │   ├── insurance_repository.py
│   │   │   ├── alert_repository.py
│   │   │   └── audit_repository.py
│   │   ├── integrations/
│   │   │   ├── __init__.py
│   │   │   ├── insurance/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── base_client.py
│   │   │   │   ├── x12_parser.py
│   │   │   │   ├── eligibility_client.py
│   │   │   │   └── schema_validator.py
│   │   │   ├── notifications/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── resend_client.py
│   │   │   │   ├── email_templates.py
│   │   │   │   └── sms_client.py
│   │   │   └── monitoring/
│   │   │       ├── __init__.py
│   │   │       ├── logfire_client.py
│   │   │       ├── metrics_collector.py
│   │   │       └── health_checker.py
│   │   ├── workers/
│   │   │   ├── __init__.py
│   │   │   ├── birthday_worker.py
│   │   │   ├── insurance_sync_worker.py
│   │   │   ├── alert_processor.py
│   │   │   └── data_quality_worker.py
│   │   ├── database/
│   │   │   ├── __init__.py
│   │   │   ├── connection.py
│   │   │   ├── migrations/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── 001_initial_schema.py
│   │   │   │   ├── 002_add_insurance_tables.py
│   │   │   │   ├── 003_add_audit_tables.py
│   │   │   │   └── 004_add_alert_system.py
│   │   │   └── seeders/
│   │   │       ├── __init__.py
│   │   │       ├── development_data.py
│   │   │       └── test_data.py
│   │   └── utils/
│   │       ├── __init__.py
│   │       ├── validators.py
│   │       ├── formatters.py
│   │       ├── date_helpers.py
│   │       ├── encryption.py
│   │       ├── file_handlers.py
│   │       └── cache.py
│   ├── tests/
│   │   ├── __init__.py
│   │   ├── conftest.py
│   │   ├── fixtures/
│   │   │   ├── __init__.py
│   │   │   ├── patient_fixtures.py
│   │   │   ├── user_fixtures.py
│   │   │   └── insurance_fixtures.py
│   │   ├── unit/
│   │   │   ├── __init__.py
│   │   │   ├── test_models/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_patient.py
│   │   │   │   └── test_user.py
│   │   │   ├── test_services/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_patient_service.py
│   │   │   │   ├── test_auth_service.py
│   │   │   │   └── test_insurance_service.py
│   │   │   └── test_utils/
│   │   │       ├── __init__.py
│   │   │       ├── test_validators.py
│   │   │       └── test_date_helpers.py
│   │   ├── integration/
│   │   │   ├── __init__.py
│   │   │   ├── test_api/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_auth.py
│   │   │   │   ├── test_patients.py
│   │   │   │   └── test_dashboard.py
│   │   │   ├── test_database/
│   │   │   │   ├── __init__.py
│   │   │   │   ├── test_patient_repository.py
│   │   │   │   └── test_user_repository.py
│   │   │   └── test_integrations/
│   │   │       ├── __init__.py
│   │   │       ├── test_insurance_client.py
│   │   │       └── test_notification_service.py
│   │   └── e2e/
│   │       ├── __init__.py
│   │       ├── test_patient_workflow.py
│   │       ├── test_auth_workflow.py
│   │       └── test_alert_workflow.py
│   ├── scripts/
│   │   ├── start_dev.py
│   │   ├── start_prod.py
│   │   ├── migrate_db.py
│   │   ├── seed_db.py
│   │   ├── backup_db.py
│   │   └── health_check.py
│   └── alembic/
│       ├── alembic.ini
│       ├── env.py
│       ├── script.py.mako
│       └── versions/
├── frontend/
│   ├── package.json
│   ├── package-lock.json
│   ├── tsconfig.json
│   ├── tailwind.config.js
│   ├── next.config.js
│   ├── .eslintrc.json
│   ├── .prettierrc
│   ├── postcss.config.js
│   ├── components.json
│   ├── public/
│   │   ├── favicon.ico
│   │   ├── logo.svg
│   │   ├── icons/
│   │   │   ├── alert.svg
│   │   │   ├── patient.svg
│   │   │   ├── dashboard.svg
│   │   │   └── settings.svg
│   │   └── images/
│   │       ├── hero-bg.jpg
│   │       └── default-avatar.png
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx
│   │   │   ├── loading.tsx
│   │   │   ├── error.tsx
│   │   │   ├── not-found.tsx
│   │   │   ├── globals.css
│   │   │   ├── (auth)/
│   │   │   │   ├── login/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── register/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   ├── (dashboard)/
│   │   │   │   ├── dashboard/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── patients/
│   │   │   │   │   ├── page.tsx
│   │   │   │   │   ├── [id]/
│   │   │   │   │   │   ├── page.tsx
│   │   │   │   │   │   └── edit/
│   │   │   │   │   │       └── page.tsx
│   │   │   │   │   └── new/
│   │   │   │   │       └── page.tsx
│   │   │   │   ├── alerts/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── reports/
│   │   │   │   │   └── page.tsx
│   │   │   │   ├── settings/
│   │   │   │   │   └── page.tsx
│   │   │   │   └── layout.tsx
│   │   │   └── api/
│   │   │       ├── auth/
│   │   │       │   └── [...nextauth]/
│   │   │       │       └── route.ts
│   │   │       └── webhooks/
│   │   │           └── insurance/
│   │   │               └── route.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.tsx
│   │   │   │   ├── input.tsx
│   │   │   │   ├── select.tsx
│   │   │   │   ├── textarea.tsx
│   │   │   │   ├── card.tsx
│   │   │   │   ├── table.tsx
│   │   │   │   ├── dialog.tsx
│   │   │   │   ├── toast.tsx
│   │   │   │   ├── alert.tsx
│   │   │   │   ├── badge.tsx
│   │   │   │   ├── avatar.tsx
│   │   │   │   ├── dropdown-menu.tsx
│   │   │   │   ├── pagination.tsx
│   │   │   │   ├── skeleton.tsx
│   │   │   │   └── loading-spinner.tsx
│   │   │   ├── layout/
│   │   │   │   ├── header.tsx
│   │   │   │   ├── sidebar.tsx
│   │   │   │   ├── footer.tsx
│   │   │   │   ├── navigation.tsx
│   │   │   │   └── breadcrumbs.tsx
│   │   │   ├── dashboard/
│   │   │   │   ├── dashboard-overview.tsx
│   │   │   │   ├── stats-cards.tsx
│   │   │   │   ├── patient-stats-chart.tsx
│   │   │   │   ├── recent-activity.tsx
│   │   │   │   ├── alerts-summary.tsx
│   │   │   │   └── quick-actions.tsx
│   │   │   ├── patients/
│   │   │   │   ├── patient-list.tsx
│   │   │   │   ├── patient-card.tsx
│   │   │   │   ├── patient-form.tsx
│   │   │   │   ├── patient-detail-view.tsx
│   │   │   │   ├── patient-search.tsx
│   │   │   │   ├── patient-filters.tsx
│   │   │   │   ├── patient-status-badge.tsx
│   │   │   │   ├── patient-bulk-actions.tsx
│   │   │   │   └── patient-insurance-info.tsx
│   │   │   ├── alerts/
│   │   │   │   ├── alert-list.tsx
│   │   │   │   ├── alert-card.tsx
│   │   │   │   ├── alert-filters.tsx
│   │   │   │   ├── birthday-alerts.tsx
│   │   │   │   ├── status-alerts.tsx
│   │   │   │   └── urgent-alerts.tsx
│   │   │   ├── forms/
│   │   │   │   ├── patient-form/
│   │   │   │   │   ├── personal-info.tsx
│   │   │   │   │   ├── address-info.tsx
│   │   │   │   │   ├── insurance-info.tsx
│   │   │   │   │   └── form-validation.tsx
│   │   │   │   ├── search-form.tsx
│   │   │   │   └── filter-form.tsx
│   │   │   ├── auth/
│   │   │   │   ├── login-form.tsx
│   │   │   │   ├── register-form.tsx
│   │   │   │   ├── forgot-password-form.tsx
│   │   │   │   └── auth-guard.tsx
│   │   │   └── common/
│   │   │       ├── loading-state.tsx
│   │   │       ├── error-boundary.tsx
│   │   │       ├── data-table.tsx
│   │   │       ├── search-input.tsx
│   │   │       ├── date-picker.tsx
│   │   │       ├── status-indicator.tsx
│   │   │       └── confirmation-dialog.tsx
│   │   ├── lib/
│   │   │   ├── utils.ts
│   │   │   ├── cn.ts
│   │   │   ├── api.ts
│   │   │   ├── auth.ts
│   │   │   ├── storage.ts
│   │   │   ├── constants.ts
│   │   │   ├── validations.ts
│   │   │   ├── date-utils.ts
│   │   │   ├── format-utils.ts
│   │   │   └── error-handler.ts
│   │   ├── hooks/
│   │   │   ├── use-auth.ts
│   │   │   ├── use-patients.ts
│   │   │   ├── use-alerts.ts
│   │   │   ├── use-local-storage.ts
│   │   │   ├── use-debounce.ts
│   │   │   ├── use-pagination.ts
│   │   │   ├── use-filters.ts
│   │   │   └── use-websocket.ts
│   │   ├── context/
│   │   │   ├── auth-context.tsx
│   │   │   ├── patient-context.tsx
│   │   │   ├── alert-context.tsx
│   │   │   └── theme-context.tsx
│   │   ├── types/
│   │   │   ├── index.ts
│   │   │   ├── patient.ts
│   │   │   ├── user.ts
│   │   │   ├── auth.ts
│   │   │   ├── alert.ts
│   │   │   ├── insurance.ts
│   │   │   └── api.ts
│   │   ├── styles/
│   │   │   ├── globals.css
│   │   │   ├── components.css
│   │   │   └── utilities.css
│   │   └── middleware.ts
│   ├── __tests__/
│   │   ├── __mocks__/
│   │   │   ├── next-auth.ts
│   │   │   └── api-responses.ts
│   │   ├── components/
│   │   │   ├── ui/
│   │   │   │   ├── button.test.tsx
│   │   │   │   └── input.test.tsx
│   │   │   ├── patients/
│   │   │   │   ├── patient-list.test.tsx
│   │   │   │   └── patient-form.test.tsx
│   │   │   └── dashboard/
│   │   │       └── dashboard-overview.test.tsx
│   │   ├── hooks/
│   │   │   ├── use-auth.test.ts
│   │   │   └── use-patients.test.ts
│   │   ├── pages/
│   │   │   ├── dashboard.test.tsx
│   │   │   └── patients.test.tsx
│   │   └── utils/
│   │       ├── api.test.ts
│   │       └── validations.test.ts
│   ├── e2e/
│   │   ├── playwright.config.ts
│   │   ├── auth.spec.ts
│   │   ├── patients.spec.ts
│   │   ├── dashboard.spec.ts
│   │   └── alerts.spec.ts
│   └── .storybook/
│       ├── main.ts
│       ├── preview.ts
│       └── stories/
│           ├── Button.stories.ts
│           ├── PatientCard.stories.ts
│           └── Dashboard.stories.ts
├── infrastructure/
│   ├── terraform/
│   │   ├── main.tf
│   │   ├── variables.tf
│   │   ├── outputs.tf
│   │   ├── versions.tf
│   │   ├── modules/
│   │   │   ├── database/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   ├── networking/
│   │   │   │   ├── main.tf
│   │   │   │   ├── variables.tf
│   │   │   │   └── outputs.tf
│   │   │   └── security/
│   │   │       ├── main.tf
│   │   │       ├── variables.tf
│   │   │       └── outputs.tf
│   │   └── environments/
│   │       ├── development/
│   │       │   ├── main.tf
│   │       │   └── terraform.tfvars
│   │       ├── staging/
│   │       │   ├── main.tf
│   │       │   └── terraform.tfvars
│   │       └── production/
│   │           ├── main.tf
│   │           └── terraform.tfvars
│   ├── docker/
│   │   ├── backend.Dockerfile
│   │   ├── frontend.Dockerfile
│   │   ├── nginx.Dockerfile
│   │   └── docker-compose.override.yml
│   ├── kubernetes/
│   │   ├── namespace.yaml
│   │   ├── configmap.yaml
│   │   ├── secrets.yaml
│   │   ├── deployment.yaml
│   │   ├── service.yaml
│   │   ├── ingress.yaml
│   │   ├── hpa.yaml
│   │   └── monitoring/
│   │       ├── servicemonitor.yaml
│   │       └── grafana-dashboard.yaml
│   └── scripts/
│       ├── deploy.sh
│       ├── backup.sh
│       ├── restore.sh
│       ├── setup-monitoring.sh
│       └── health-check.sh
├── monitoring/
│   ├── logfire/
│   │   ├── config.yaml
│   │   ├── dashboards/
│   │   │   ├── application-metrics.json
│   │   │   ├── infrastructure-metrics.json
│   │   │   └── business-metrics.json
│   │   └── alerts/
│   │       ├── application-alerts.yaml
│   │       └── infrastructure-alerts.yaml
│   ├── grafana/
│   │   ├── dashboards/
│   │   │   ├── system-overview.json
│   │   │   ├── api-performance.json
│   │   │   └── user-activity.json
│   │   └── provisioning/
│   │       ├── dashboards.yaml
│   │       └── datasources.yaml
│   └── prometheus/
│       ├── prometheus.yml
│       ├── rules/
│       │   ├── application.yml
│       │   └── infrastructure.yml
│       └── targets/
│           ├── api-targets.json
│           └── frontend-targets.json
├── data/
│   ├── insurance_data_source/
│   │   ├── README.md
│   │   ├── auth_config.json
│   │   ├── data_mapping.json
│   │   ├── eligibility_schema.xml
│   │   ├── secure_client_demo.py
│   │   └── patient_*.xml (files 001-020)
│   ├── sample_data/
│   │   ├── patients.json
│   │   ├── providers.json
│   │   └── insurance_plans.json
│   └── migrations/
│       ├── 001_initial_schema.sql
│       ├── 002_insurance_integration.sql
│       └── 003_audit_system.sql
├── security/
│   ├── policies/
│   │   ├── data-protection.md
│   │   ├── access-control.md
│   │   └── incident-response.md
│   ├── certificates/
│   │   ├── README.md
│   │   └── .gitkeep
│   ├── secrets/
│   │   ├── .env.development
│   │   ├── .env.staging
│   │   └── .env.production.example
│   └── compliance/
│       ├── hipaa-compliance.md
│       ├── audit-procedures.md
│       └── security-checklist.md
└── tools/
    ├── scripts/
    │   ├── setup-dev-env.sh
    │   ├── generate-test-data.py
    │   ├── backup-database.sh
    │   ├── restore-database.sh
    │   └── performance-test.py
    ├── generators/
    │   ├── component-generator.js
    │   ├── api-generator.py
    │   └── test-generator.py
    └── linting/
        ├── .eslintrc.js
        ├── .pylintrc
        ├── .pre-commit-config.yaml
        └── prettier.config.js
