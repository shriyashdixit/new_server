#!/bin/bash
set -o allexport
source /home/puneserver/new_server/.env.prod.telegram
set +o allexport
# --- CONFIGURATION ---


DAILY_SUMMARY_TIME="09:00"  # 24-hour format

# --- SYSTEM INFO ---
HOSTNAME=$(hostname)
IP_ADDRESS=$(hostname -I | awk '{print $1}')
NOW=$(date '+%Y-%m-%d %H:%M:%S')

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

# 1. Check if WireGuard Interface Exists
if ! ip link show "$WG_INTERFACE" > /dev/null 2>&1; then
    send_telegram_message "🚨 *WireGuard Interface \`$WG_INTERFACE\` Not Found!* Please manually investigate and restart WireGuard service."
    exit 1
fi

# 2. Check Interface Status
if ! wg show "$WG_INTERFACE" > /dev/null 2>&1; then
    send_telegram_message "🚨 *WireGuard Interface \`$WG_INTERFACE\` is DOWN or NOT responding!* Manual intervention required!"
    exit 1
fi


# 3. Gather Peer Info
PEER_INFO=$(wg show "$WG_INTERFACE" dump)
IFS=$'\n' read -rd '' -a PEERS <<<"$PEER_INFO"
HEADER=${PEERS[0]}
unset PEERS[0]

CONNECTED_PEERS=""
TOTAL_UPLOAD=0
TOTAL_DOWNLOAD=0

NEW_CONNECTIONS=()
DISCONNECTIONS=()

mkdir -p "$(dirname "$LAST_HANDSHAKE_FILE")"
touch "$LAST_HANDSHAKE_FILE"

for PEER in "${PEERS[@]}"; do
    FIELDS=($PEER)
    PUBLIC_KEY="${FIELDS[0]}"
    LAST_HANDSHAKE="${FIELDS[5]}"
    RX_BYTES="${FIELDS[6]}"
    TX_BYTES="${FIELDS[7]}"

    # Calculate total traffic
    TOTAL_UPLOAD=$((TOTAL_UPLOAD + TX_BYTES))
    TOTAL_DOWNLOAD=$((TOTAL_DOWNLOAD + RX_BYTES))

    # Convert last handshake
    if [ "$LAST_HANDSHAKE" -gt 0 ]; then
        LAST_SEEN=$(date -d "@$LAST_HANDSHAKE" '+%Y-%m-%d %H:%M:%S')
        NAME=$(get_peer_name "$PUBLIC_KEY")
        CONNECTED_PEERS+="- \`$NAME\` — Last Seen: *$LAST_SEEN*, Uploaded: *$((TX_BYTES/1048576)) MB*, Downloaded: *$((RX_BYTES/1048576)) MB*%0A"
    fi

    # --- Detect Connections/Disconnections ---
    LAST_HANDSHAKE_PREV=$(grep "$PUBLIC_KEY" "$LAST_HANDSHAKE_FILE" | awk '{print $2}')
    if [ -z "$LAST_HANDSHAKE_PREV" ]; then
        echo "$PUBLIC_KEY $LAST_HANDSHAKE" >> "$LAST_HANDSHAKE_FILE"
    else
        if [ "$LAST_HANDSHAKE" != "$LAST_HANDSHAKE_PREV" ]; then
            if [ "$LAST_HANDSHAKE" -gt "$LAST_HANDSHAKE_PREV" ]; then
                NAME=$(get_peer_name "$PUBLIC_KEY")
                NEW_CONNECTIONS+=("$NAME")
            fi
            sed -i "s|$PUBLIC_KEY .*|$PUBLIC_KEY $LAST_HANDSHAKE|" "$LAST_HANDSHAKE_FILE"
        fi
    fi
done

# 4. Format totals
TOTAL_UPLOAD_MB=$((TOTAL_UPLOAD/1048576))
TOTAL_DOWNLOAD_MB=$((TOTAL_DOWNLOAD/1048576))

# 5. Send Connection Notifications Immediately
if [ ${#NEW_CONNECTIONS[@]} -gt 0 ]; then
  MESSAGE="🔔 *New WireGuard Connection(s) Detected:*%0A"
  for user in "${NEW_CONNECTIONS[@]}"; do
    MESSAGE+="➔ \`$user\` connected%0A"
  done
  send_telegram_message "$MESSAGE"
fi

# 6. Send Daily Summary at 9 AM
CURRENT_TIME=$(date '+%H:%M')

if [ "$CURRENT_TIME" = "$DAILY_SUMMARY_TIME" ]; then
  SUMMARY="🔒 *WireGuard VPN Daily Summary*
📅 *Time:* \`$NOW\`
🌐 *Interface:* \`$WG_INTERFACE\` (UP ✅)
📈 *Total Traffic:* Upload: \`${TOTAL_UPLOAD_MB} MB\`, Download: \`${TOTAL_DOWNLOAD_MB} MB\`

👥 *Connected Peers:*
$CONNECTED_PEERS"

  send_telegram_message "$SUMMARY"
fi
