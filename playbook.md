# Mosquitto MQTT i docker

Her sætter jeg op i docker, men kan måske også bruges direkte på raspberry pi, uden docker.

## Inspiration

I første hug inspireret på vejledningen på <https://www.datacamp.com/tutorial/mosquitto-docker>

### laver mapper

    mkdir ./mosquitto/config
    mkdir ./mosquitto/data
    mkdir ./mosquitto/log

### opret `docker-compose.yaml`

```
# Basic listener configuration
listener 1883
allow_anonymous true

# WebSocket listener
listener 9001
protocol websockets
allow_anonymous true

# Persistence
persistence true
persistence_location /mosquitto/data/

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_type error
log_type warning
log_type notice
log_type information
```

### opret git og put på github

Her brugte jeg gui i VSCode, men det er noget i retning af:

    git init
    git add .
    git commit -m "first"
    git add remote ...

### opret placeholder filer

git opretter ikke tomme mapper, så jeg putter en tom `.gitkeep` i hver af mapperne. \
Min win11 har ikke __touch__ installeret men hvis den var kunne jeg have skrevet:

    touch .\mosquitto\config\.gitkeep
    touch .\mosquitto\data\.gitkeep
    touch .\mosquitto\log\.gitkeep

### første start og hul-igennem-test

start

    docker-compose up -d

( hvis ikke det spiller, kan man prøve uden `-d`)

# vibe-coder lidt

Jeg ønsker en løsning med MQTT (som vi har allerede) og et script til at hente __alle__ messages i __alle__ topics, over i mapper/filer med samme navn som topic (tror jeg).
Jeg har chattet lidt frem og tilbage, og fortsætter her...

---

### Prompt fortsætter...

> Ja det er virkelig nyttigt, på en dedikret linux maskine, men jeg vil gerne afvikle mqtt, nginx og MQTT logger scriptet i docker,  og docker-compose. Jeg har allerede en service med Mosquitto. Hvordan setter jeg dette op med nginx og en service med dataloggeren i python?

---

Perfekt! Her er en komplet Docker Compose løsning:

## Mappestruktur
```
mqtt-project/
├── docker-compose.yml
├── mosquitto/
│   └── mosquitto.conf
├── logger/
│   ├── Dockerfile
│   └── mqtt_logger.py
└── nginx/
    └── nginx.conf
```

## docker-compose.yml
```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto-data:/mosquitto/data
      - mosquitto-logs:/mosquitto/log
    restart: unless-stopped

  mqtt-logger:
    build: ./logger
    container_name: mqtt-logger
    depends_on:
      - mosquitto
    volumes:
      - mqtt-logs:/var/mqtt_logs
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: mqtt-nginx
    ports:
      - "8080:80"
    volumes:
      - mqtt-logs:/usr/share/nginx/html:ro
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped

volumes:
  mosquitto-data:
  mosquitto-logs:
  mqtt-logs:
```

## mosquitto/mosquitto.conf
```conf
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

## logger/Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir paho-mqtt

COPY mqtt_logger.py .

CMD ["python", "-u", "mqtt_logger.py"]
```

## logger/mqtt_logger.py
```python
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
```

## nginx/nginx.conf
```nginx
server {
    listen 80;
    server_name _;
    
    location / {
        root /usr/share/nginx/html;
        autoindex on;
        autoindex_exact_size off;
        autoindex_localtime on;
        
        # Vis .jsonl filer som tekst
        types {
            text/plain jsonl;
        }
        
        charset utf-8;
        
        # CORS hvis eleverne skal tilgå fra andre domæner
        add_header Access-Control-Allow-Origin *;
    }
}
```

## Start det hele
```bash
docker-compose up -d
```

## Test det virker
```bash
# Publish en test-besked
docker exec mqtt-broker mosquitto_pub -t "test/topic" -m "Hello World"

# Se logs fra logger
docker logs -f mqtt-logger

# Tjek i browser
# Gå til http://localhost:8080
```

## Nyttige kommandoer
```bash
# Se alle logs
docker-compose logs -f

# Genstart en service
docker-compose restart mqtt-logger

# Stop alt
docker-compose down

# Stop alt og slet volumes (sletter alle logged data!)
docker-compose down -v
```

Nu har du alt kørende i Docker med data persistent i volumes! Eleverne kan tilgå `http://din-server:8080` for at se deres MQTT data. 🎉

--- 

### mere prompt

> Jeg synes mosquitto.conf skal ligge i mqtt-projekt/mosquitto/conf/mosquitto.conf, for det passer den demo jeg har set på https://www.datacamp.com/tutorial/mosquitto-docker

---

God idé at følge en standardiseret struktur! Her er den opdaterede version:

## Mappestruktur
```
mqtt-project/
├── docker-compose.yml
├── mosquitto/
│   └── conf/
│       └── mosquitto.conf
├── logger/
│   ├── Dockerfile
│   └── mqtt_logger.py
└── nginx/
    └── nginx.conf
```

## Opdateret docker-compose.yml
```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"
      - "9001:9001"
    volumes:
      - ./mosquitto/conf/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - mosquitto-data:/mosquitto/data
      - mosquitto-logs:/mosquitto/log
    restart: unless-stopped

  mqtt-logger:
    build: ./logger
    container_name: mqtt-logger
    depends_on:
      - mosquitto
    volumes:
      - mqtt-logs:/var/mqtt_logs
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    restart: unless-stopped

  nginx:
    image: nginx:alpine
    container_name: mqtt-nginx
    ports:
      - "8080:80"
    volumes:
      - mqtt-logs:/usr/share/nginx/html:ro
      - ./nginx/nginx.conf:/etc/nginx/conf.d/default.conf:ro
    restart: unless-stopped

volumes:
  mosquitto-data:
  mosquitto-logs:
  mqtt-logs:
```

## mosquitto/conf/mosquitto.conf
```conf
listener 1883
allow_anonymous true
persistence true
persistence_location /mosquitto/data/
log_dest file /mosquitto/log/mosquitto.log
```

Resten af filerne forbliver de samme. Nu matcher strukturen DataCamp's tutorial! 👍

---

Så nu prøver jeg at kopiere alle tingene ud i de rigtige filer, og se om det kan køre...

efter meget chat virker det nu. Se git []()

---

# Promt

> ... jeg vil også gerne at Mosquitto mqtt både accepterer annomyme opkald, og med password
---

Ah, det giver god mening! Så skal du have:
- Port 1883: Anonym (usikret)
- Port 8883: SSL/TLS med brugernavn + password (sikret)

Her er hvordan:

## 1. Opret SSL certifikater

Først skal vi generere self-signed certificates:

```bash
# Opret certs mappe
mkdir -p mosquitto/certs
cd mosquitto/certs

# Generer CA (Certificate Authority)
openssl req -new -x509 -days 3650 -extensions v3_ca -keyout ca.key -out ca.crt -subj "/CN=MQTT-CA"

# Generer server key og certificate signing request
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=localhost"

# Sign server certificate med CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650

# Cleanup
rm server.csr ca.srl

cd ../..
```

## 2. Opdater mosquitto.conf

```conf
# Anonym listener på port 1883 (usikret)
listener 1883
allow_anonymous true

# Authenticated listener på port 8883 (SSL/TLS)
listener 8883
allow_anonymous false
password_file /mosquitto/config/password.txt

# SSL/TLS certifikater
cafile /mosquitto/certs/ca.crt
certfile /mosquitto/certs/server.crt
keyfile /mosquitto/certs/server.key

# TLS version (valgfrit, kun moderne versioner)
tls_version tlsv1.2

# Persistence
persistence true
persistence_location /mosquitto/data/

# Logging
log_dest file /mosquitto/log/mosquitto.log
log_dest stdout
```

## 3. Opdater docker-compose.yml

```yaml
version: '3.8'

services:
  mosquitto:
    image: eclipse-mosquitto:latest
    container_name: mqtt-broker
    ports:
      - "1883:1883"   # Anonym
      - "8883:8883"   # SSL/TLS
      - "9001:9001"   # WebSocket (valgfrit)
    volumes:
      - ./mosquitto/conf/mosquitto.conf:/mosquitto/config/mosquitto.conf
      - ./mosquitto/conf/password.txt:/mosquitto/config/password.txt
      - ./mosquitto/certs:/mosquitto/certs:ro
      - mosquitto-data:/mosquitto/data
      - mosquitto-logs:/mosquitto/log
    restart: unless-stopped

  mqtt-logger:
    build: ./logger
    container_name: mqtt-logger
    depends_on:
      - mosquitto
    volumes:
      - mqtt-logs:/var/mqtt_logs
    environment:
      - MQTT_BROKER=mosquitto
      - MQTT_PORT=1883
    restart: unless-stopped

  nginx:
    build: ./nginx
    container_name: mqtt-nginx
    ports:
      - "8080:80"
    volumes:
      - mqtt-logs:/usr/share/nginx/html:ro
    restart: unless-stopped

volumes:
  mosquitto-data:
  mosquitto-logs:
  mqtt-logs:
```

## 4. Opret password fil

```bash
docker-compose up -d
docker exec -it mqtt-broker mosquitto_passwd -c /mosquitto/config/password.txt elev1
docker exec -it mqtt-broker mosquitto_passwd /mosquitto/config/password.txt laerer
docker-compose restart mosquitto
```

## 5. Test begge forbindelser

**Anonym på port 1883:**
```bash
docker exec mqtt-broker mosquitto_pub -h localhost -p 1883 -t "test/anonym" -m "Uden sikkerhed"
```

**Authenticated på port 8883 med TLS:**
```bash
docker exec mqtt-broker mosquitto_pub -h localhost -p 8883 \
  --cafile /mosquitto/certs/ca.crt \
  -u elev1 -P <password> \
  -t "test/sikker" -m "Med TLS og password"
```

## 6. Python client eksempel med TLS

Hvis eleverne skal connecte udefra med Python:

```python
import paho.mqtt.client as mqtt
import ssl

client = mqtt.Client()
client.username_pw_set("elev1", "password")

# Konfigurer TLS
client.tls_set(
    ca_certs="ca.crt",  # Path til CA certificate
    tls_version=ssl.PROTOCOL_TLSv1_2
)

# For self-signed certificates (kun til test!)
client.tls_insecure_set(True)

client.connect("din-server", 8883, 60)
client.publish("test/sikker", "Hello via TLS!")
```

Nu har du:
- 🔓 **Port 1883**: Anonym, usikret (til hurtig test)
- 🔐 **Port 8883**: TLS + brugernavn/password (til produktion)

Eleverne kan kopiere `ca.crt` fra `mosquitto/certs/` for at connecte med TLS! 🚀

---

## Certs

Passfrase 
: `teciotemb`

## mosquitto.conf

Måtte tilføje 
```
# Enable per-listener settings
per_listener_settings true
```
