# Udgave til at køre på Raspberry Pi

Pt. kører det på en Pi 4. Måske kan vi også køre på en 3'er.

Her gentager jeg primært de ting der er anderledes end på doscker udgaven...


### certifikater til TLS

localhost duer ikke på localnettet

```bash

# ca som sædvanligt

# Generer server key og certificate signing request
openssl genrsa -out server.key 2048
openssl req -new -key server.key -out server.csr -subj "/CN=wilson.local"

```

gentag resten

__nb__ 

Passfrase 
: `teciotemb`

```bash

# Sign server certificate med CA
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 3650

# Cleanup
rm server.csr ca.srl

cd ../..
```

#### Multidomain cert

san.cnf
```ini
[req]
distinguished_name = req_distinguished_name
req_extensions = v3_req

[req_distinguished_name]

[v3_req]
subjectAltName = @alt_names

[alt_names]
DNS.1 = wilson.local
DNS.2 = localhost
IP.1 = 127.0.0.1
IP.2 = 192.168.0.161
```

Create

    openssl req -new -newkey rsa:4096 -nodes -keyout server.key -out server.csr -subj "/CN=wilson.local" -config san.cnf


Sign

    openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 365 -sha256 -extfile san.cnf -extensions v3_req
