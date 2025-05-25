#!/bin/bash
set -o allexport
source /home/puneserver/new_server/.env.prod.telegram
set +o allexport

START_TIME_GLOBAL=$(date +%s)

# Define folders to backup
FOLDERS_ARRAY=($FOLDERS)

# Track results
RESULTS=""
ALL_SUCCESS=true

# Start backup for each folder
for FOLDER in "${FOLDERS[@]}"; do
    START_TIME_FOLDER=$(date +%s)
    
    rsync -a --delete "$SOURCE_BASE/$FOLDER/" "$DEST_BASE/backup_$FOLDER/"
    EXIT_CODE=$?
    
    END_TIME_FOLDER=$(date +%s)
    DURATION_FOLDER=$((END_TIME_FOLDER - START_TIME_FOLDER))
    
    if [ $EXIT_CODE -eq 0 ]; then
        RESULTS+="*Folder:* \`$FOLDER\` — ✅ Success (*${DURATION_FOLDER}s*)%0A"
    else
        RESULTS+="*Folder:* \`$FOLDER\` — ❌ Failed (*${DURATION_FOLDER}s*)%0A"
        ALL_SUCCESS=false
    fi
done

# Calculate total duration
END_TIME_GLOBAL=$(date +%s)
DURATION_GLOBAL=$((END_TIME_GLOBAL - START_TIME_GLOBAL))
DURATION_MINUTES=$((DURATION_GLOBAL / 60))

# Get total Backup Size
BACKUP_SIZE=$(du -sh "$DEST_BASE" | awk '{print $1}')

# Get Free Disk Space at destination
FREE_SPACE=$(df -h "$DEST_BASE" | awk 'NR==2 {print $4}')

# Get system info
HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I | awk '{print $1}')

# Prepare timestamp
NOW=$(date '+%Y-%m-%d %H:%M:%S')

# Prepare final message
if [ "$ALL_SUCCESS" = true ]; then
    STATUS="✅ *Backup Summary: All Success*"
else
    STATUS="❌ *Backup Summary: One or More Failures*"
fi

MESSAGE="*$STATUS*
📅 *Time:* \`$NOW\`
🔹 *Host:* \`$HOSTNAME\`
🌐 *IP:* \`$IP_ADDRESS\`
📁 *Total Backup Size:* \`$BACKUP_SIZE\`
💽 *Free Space:* \`$FREE_SPACE\`
⏳ *Total Duration:* \`${DURATION_MINUTES} min (${DURATION_GLOBAL}s)\`

*Folder Status:*
$RESULTS
"

# Send Telegram notification
curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
  -d chat_id="${TELEGRAM_CHAT_ID}" \
  -d parse_mode="Markdown" \
  -d text="$MESSAGE"
