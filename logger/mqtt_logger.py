import paho.mqtt.client as mqtt
import json
from datetime import datetime
from pathlib import Path
import re
import os
import time

LOG_DIR = Path("/var/mqtt_logs")
LOG_DIR.mkdir(parents=True, exist_ok=True)

MQTT_BROKER = os.getenv('MQTT_BROKER', 'localhost')
MQTT_PORT = int(os.getenv('MQTT_PORT', 1883))

def safe_filename(topic):
    """Konverter topic til gyldig filnavn"""
    return re.sub(r'[^\w\-_/]', '_', topic) + '.jsonl'

def on_connect(client, userdata, flags, rc):
    print(f"Connected to MQTT broker with result code {rc}")
    client.subscribe("#")
    print("Subscribed to all topics (#)")

def on_message(client, userdata, msg):
    try:
        payload = msg.payload.decode()
    except:
        payload = str(msg.payload)
    
    data = {
        "timestamp": datetime.now().isoformat(),
        "topic": msg.topic,
        "payload": payload
    }
    
    filename = LOG_DIR / safe_filename(msg.topic)
    with open(filename, "a") as f:
        f.write(json.dumps(data, ensure_ascii=False) + "\n")
    
    print(f"Logged: {msg.topic}")

def main():
    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    
    while True:
        try:
            print(f"Connecting to {MQTT_BROKER}:{MQTT_PORT}...")
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            client.loop_forever()
        except Exception as e:
            print(f"Connection failed: {e}. Retrying in 5 seconds...")
            time.sleep(5)

if __name__ == "__main__":
    main()

