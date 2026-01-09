#!/bin/bash

# Get absolute paths
PROJECT_DIR=$(pwd)
PYTHON_EXEC="$PROJECT_DIR/.venv/bin/python"
SCRIPT_PATH="$PROJECT_DIR/app/quant_b_module/daily_report.py"
LOG_FILE="$PROJECT_DIR/cron.log"

echo "--- Setting up Daily Report Cron Job ---"

# The Command: Run python script at 20:00 (8 PM) every day
CRON_CMD="0 20 * * * $PYTHON_EXEC $SCRIPT_PATH >> $LOG_FILE 2>&1"

# Add to crontab safely (checks if it exists first)
(crontab -l 2>/dev/null; echo "$CRON_CMD") | sort -u | crontab -

echo "Success! Cron job added:"
echo "$CRON_CMD"
