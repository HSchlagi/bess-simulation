
"""
Publish power setpoints to MS-A2 via MQTT.
Set environment variable MS_A2_DEVICE_ID and publish at an interval under 59 seconds while EMS mode is "mqtt_ctrl".
"""
import os, time, yaml
import paho.mqtt.client as mqtt
import random

def main():
    with open("config.yaml","r",encoding="utf-8") as f:
        cfg = yaml.safe_load(f)
    dev_id = os.getenv("MS_A2_DEVICE_ID", "MSA-XXXXXXXXXXXXXXXXX")
    mcfg = cfg["mqtt"]
    base = f"homeassistant/number/{dev_id}/power_ctrl/set"
    client = mqtt.Client(client_id=mcfg.get("client_id","bess-msa2-ctrl"))
    if mcfg.get("username"):
        client.username_pw_set(mcfg["username"], mcfg.get("password",""))
    client.connect(mcfg["broker"], mcfg.get("port",1883), keepalive=60)
    client.loop_start()
    setpoint = float(os.getenv("MS_A2_SETPOINT_W", "0"))
    interval = float(os.getenv("MS_A2_INTERVAL_S", "55"))  # keep below 60s
    jitter = float(os.getenv("MS_A2_JITTER_W", "0.1"))     # change decimal each publish
    print(f"Publishing {setpoint} W every {interval}s to {base}")
    try:
        while True:
            # add tiny jitter to keep device in mqtt_ctrl
            jittered = setpoint + (random.choice([-1,1]) * jitter)
            client.publish(base, str(jittered), qos=0, retain=False)
            time.sleep(interval)
    finally:
        client.loop_stop()

if __name__ == "__main__":
    main()
