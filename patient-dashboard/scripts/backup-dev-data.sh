#!/bin/bash
# Backup Development Data Script

TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_DIR="./backups/dev/${TIMESTAMP}"

echo "📦 Backing up development data..."

# Create backup directory
mkdir -p ${BACKUP_DIR}

# Backup development database
if [ -d "./data/dev-surrealdb" ]; then
    echo "💾 Backing up development database..."
    cp -r ./data/dev-surrealdb ${BACKUP_DIR}/
fi

# Backup development environment files
echo "📄 Backing up development configuration..."
cp .env.development ${BACKUP_DIR}/
cp ./backend/.env.development ${BACKUP_DIR}/backend.env.development
cp ./frontend/.env.development ${BACKUP_DIR}/frontend.env.development

# Create backup info file
echo "📝 Creating backup manifest..."
cat > ${BACKUP_DIR}/backup-info.txt << EOF
Backup Created: ${TIMESTAMP}
Environment: Development
Database: patient_dashboard_dev
Namespace: patient_dashboard_dev
EOF

echo "✅ Development backup complete: ${BACKUP_DIR}"