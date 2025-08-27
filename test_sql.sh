#!/bin/bash
# Test script to execute ALTER TABLE command

echo "Testing SQL ALTER TABLE command..."

# Try with SQLite (create test database first)
echo "Creating test database and users table..."
sqlite3 test.db "CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY, name TEXT);"

echo "Executing ALTER TABLE command..."
sqlite3 test.db "ALTER TABLE users ADD COLUMN email VARCHAR(255);"

if [ $? -eq 0 ]; then
    echo "SUCCESS: ALTER TABLE command executed successfully"
    echo "Verifying table structure:"
    sqlite3 test.db ".schema users"
else
    echo "FAILED: ALTER TABLE command failed"
fi

# Clean up
rm -f test.db