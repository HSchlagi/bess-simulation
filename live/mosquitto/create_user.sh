#!/bin/sh
set -e
USER_NAME=${1:-bessuser}
PASSFILE="/mosquitto/config/passwords"
if [ ! -f "$PASSFILE" ]; then
  touch "$PASSFILE"
fi
echo "Creating/Updating MQTT user: $USER_NAME"
mosquitto_passwd -c "$PASSFILE" "$USER_NAME"
chown mosquitto:mosquitto "$PASSFILE"
chmod 600 "$PASSFILE"
echo "Done. Restart mosquitto if running."
