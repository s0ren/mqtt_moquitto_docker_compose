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

