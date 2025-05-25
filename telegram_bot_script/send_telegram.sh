#!/bin/bash
set -o allexport
source /home/puneserver/new_server/.env.prod.telegram
set +o allexport

MESSAGE=$1

curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
    -d chat_id="${TELEGRAM_CHAT_ID}" \
    -d text="$MESSAGE"
