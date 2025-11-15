# oneline cmd test

<https://www.datacamp.com/tutorial/mosquitto-docker#using-mosquitto_pub-and-mosquitto_sub-the%3Cc>

Uden at installere andet end det docker setup vi allerede har, kan man køre disse:

    # Subscribe using the container
    docker exec -it mosquitto mosquitto_sub -h localhost -t test/topic

    # Publish using the container
    docker exec -it mosquitto mosquitto_pub -h localhost -t test/topic -m "Container message"

I praksis er det federe at installere mere...
