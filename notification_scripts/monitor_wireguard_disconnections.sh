#!/bin/bash
set -o allexport
source /home/puneserver/new_server/.env.prod.telegram
set +o allexport


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
mkdir -p "$(dirname "$LAST_CONNECTED_FILE")"
touch "$LAST_CONNECTED_FILE"

# Get current connected peers
CONNECTED_NOW=()
PEER_INFO=$(wg show "$WG_INTERFACE" latest-handshakes)

while read -r line; do
    public_key=$(echo "$line" | awk '{print $1}')
    last_handshake=$(echo "$line" | awk '{print $2}')
    current_time=$(date +%s)
    delta=$((current_time - last_handshake))

    # If handshake was within last 180 seconds (3 min), consider connected
    if [ "$last_handshake" -gt 0 ] && [ "$delta" -lt 180 ]; then
        CONNECTED_NOW+=("$public_key")
    fi
done <<< "$PEER_INFO"

# Compare with last connected peers
if [ -f "$LAST_CONNECTED_FILE" ]; then
    mapfile -t LAST_CONNECTED < "$LAST_CONNECTED_FILE"
else
    LAST_CONNECTED=()
fi

# Detect disconnections
for peer in "${LAST_CONNECTED[@]}"; do
    if [[ ! " ${CONNECTED_NOW[@]} " =~ " ${peer} " ]]; then
        name=$(get_peer_name "$peer")
        send_telegram_message "🔌 *WireGuard Peer Disconnected:* \`$name\`"
    fi
done

# Save current connected peers
printf "%s\n" "${CONNECTED_NOW[@]}" > "$LAST_CONNECTED_FILE"
