# Simple MQTT Publisher to test the ingestion path
import json, paho.mqtt.client as mqtt

BROKER = "localhost"
PORT = 1883
USER = "bessuser"
PASS = "besspass"
TOPIC = "bess/site1/bess1/telemetry"

payload = {
    "ts": "2025-01-01T00:00:00Z",
    "site": "site1",
    "device": "bess1",
    "soc": 57.1,
    "p": -120.0,
    "p_dis": 120.0,
    "v_dc": 780.5,
    "i_dc": 160.2,
    "t_cell_max": 31.5,
    "soh": 98.6,
    "alarms": []
}

cli = mqtt.Client()
cli.username_pw_set(USER, PASS)
cli.connect(BROKER, PORT, 60)
cli.publish(TOPIC, json.dumps(payload), qos=1)
print("Published sample payload.")
cli.disconnect()
