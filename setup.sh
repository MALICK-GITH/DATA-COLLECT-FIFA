#!/bin/bash

# Setup script for Match Saver Cron Job

echo "Setting up Match Saver Cron Job..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOL
# Database Configuration
DB_TYPE=sqlite
SQLITE_PATH=match_history.db

# For PostgreSQL, uncomment and configure:
# DB_TYPE=postgresql
# DB_HOST=localhost
# DB_PORT=5432
# DB_NAME=match_history
# DB_USER=postgres
# DB_PASSWORD=your_password

# Cron Configuration
CRON_SCHEDULE=*/5 * * * *

# Logging
LOG_LEVEL=INFO
LOG_FILE=match_saver.log
EOL
fi

# Create database tables
echo "Creating database tables..."
python -c "from database import DatabaseManager; db = DatabaseManager(); db.create_tables()"

echo "Setup complete!"
echo ""
echo "To run the scraper once: python scraper.py"
echo "To run the cron service: python cron_service.py"
echo ""
echo "To set up system cron job, see cron_setup.txt"
