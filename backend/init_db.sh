#!/bin/sh

DB_FILE="sages.db"

if [ ! -f "$DB_FILE" ]; then
    echo "Database not found. Creating $DB_FILE ..."

    python init_tables.py
    python init.py

    if [ $? -eq 0 ]; then
        echo "Database created and initialized successfully."
    else
        echo "Error: Failed to initialize database."
        exit 1
    fi
else
    echo "Database already exists. No action taken."
fi



