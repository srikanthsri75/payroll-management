#!/bin/bash
# Employee Details Migration Script
# Run this script to update existing database with new employee fields

# Load environment variables if .env file exists
if [ -f .env ]; then
    set -o allexport
    source .env
    set +o allexport
fi

# Database connection parameters
MYSQL_USER=${MYSQL_USER:-root}
MYSQL_PASSWORD=${MYSQL_PASSWORD:-mysqlServer9.5.0}
MYSQL_HOST=${MYSQL_HOST:-localhost}
MYSQL_DB=${MYSQL_DB:-payroll_db}

echo "Running employee details migration..."
echo "Database: $MYSQL_DB on $MYSQL_HOST"

# Run the migration script
mysql -u "$MYSQL_USER" -p"$MYSQL_PASSWORD" -h "$MYSQL_HOST" "$MYSQL_DB" < ../scripts/004_add_employee_details.sql

if [ $? -eq 0 ]; then
    echo "✓ Employee details migration completed successfully"
    echo "New fields added to employees table:"
    echo "  - date_of_birth"
    echo "  - gender"
    echo "  - marital_status"
    echo "  - national_id"
    echo "  - tax_id"
    echo "  - address"
    echo "  - emergency_contact_name"
    echo "  - emergency_contact_phone"
    echo "  - employment_type"
    echo ""
    echo "Indexes created for optimized searching"
else
    echo "✗ Migration failed. Please check database connection and permissions."
    exit 1
fi