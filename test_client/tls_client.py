import paho.mqtt.client as mqtt
import ssl
# from pathlib import Path

# CERT_PATH = Path()

client = mqtt.Client()
client.username_pw_set("elev1", "password")



# Konfigurer TLS
client.tls_set(
    ca_certs="ca.crt",  # Path til CA certificate
    tls_version=ssl.PROTOCOL_TLSv1_2
)

# For self-signed certificates (kun til test!)
# client.tls_insecure_set(True)

client.connect("localhost", 8883, 60)
client.publish("test/sikker", "Hello via TLS, fra ekstern klient!")