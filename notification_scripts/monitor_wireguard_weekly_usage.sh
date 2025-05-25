#!/bin/bash
set -o allexport
source /home/puneserver/new_server/.env.prod.telegram
set +o allexport
# --- CONFIGURATION ---


# --- FUNCTIONS ---
send_telegram_message() {
  local message="$1"
  curl -s -X POST "https://api.telegram.org/bot${TELEGRAM_BOT_TOKEN}/sendMessage" \
      -d chat_id="${TELEGRAM_CHAT_ID}" \
      -d parse_mode="Markdown" \
      -d text="$message"
}

get_peer_name() {
  local public_key="$1"
  local name
  name=$(grep "$public_key" "$PEER_MAPPING_FILE" | awk -F "=" '{print $2}')
  if [ -z "$name" ]; then
    echo "$public_key"
  else
    echo "$name"
  fi
}

# --- MAIN LOGIC ---
HOSTNAME=$(hostname)
NOW=$(date '+%Y-%m-%d %H:%M:%S')

PEER_INFO=$(wg show "$WG_INTERFACE" dump)
IFS=$'\n' read -rd '' -a PEERS <<<"$PEER_INFO"
unset PEERS[0]  # remove header

MESSAGE="📈 *WireGuard Weekly Traffic Report*%0A📅 *Time:* \`$NOW\`%0A🔹 *Host:* \`$HOSTNAME\`%0A%0A"

for PEER in "${PEERS[@]}"; do
    FIELDS=($PEER)
    PUBLIC_KEY="${FIELDS[0]}"
    RX_BYTES="${FIELDS[6]}"
    TX_BYTES="${FIELDS[7]}"

    RX_MB=$((RX_BYTES/1048576))
    TX_MB=$((TX_BYTES/1048576))

    NAME=$(get_peer_name "$PUBLIC_KEY")
    MESSAGE+="➔ \`$NAME\` — Uploaded: *${TX_MB} MB*, Downloaded: *${RX_MB} MB*%0A"
done

send_telegram_message "$MESSAGE"
