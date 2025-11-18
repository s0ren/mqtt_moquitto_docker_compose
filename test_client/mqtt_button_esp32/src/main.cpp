#include <Arduino.h>
#include <WiFi.h>
#include <PubSubClient.h>

// WiFi indstillinger
const char* ssid = "IoT_H3/4";
const char* password = "98806829";

// MQTT indstillinger
const char* mqtt_server = "wilson.local";  // f.eks. "192.168.1.100"
const int mqtt_port = 1883;
const char* mqtt_topic = "test/esp32/button";

const int buttonPin = 32;
int lastButtonState = LOW;
int buttonState = LOW;
unsigned long lastDebounceTime = 0;
unsigned long debounceDelay = 50;

WiFiClient espClient;
PubSubClient client(espClient);

void setup_wifi() {
  Serial.println();
  Serial.print("Connecting to WiFi");
  
  WiFi.begin(ssid, password);
  
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  
  Serial.println("\nWiFi connected!");
  Serial.print("IP: ");
  Serial.println(WiFi.localIP());
}

void reconnect() {
  while (!client.connected()) {
    Serial.print("Connecting to MQTT...");
    
    String clientId = "ESP32-" + String(random(0xffff), HEX);
    
    if (client.connect(clientId.c_str())) {
      Serial.println("connected");
    } else {
      Serial.print("failed, rc=");
      Serial.println(client.state());
      delay(5000);
    }
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(buttonPin, INPUT);
  
  setup_wifi();
  client.setServer(mqtt_server, mqtt_port);
  
  Serial.println("ESP32 ready!");
}

void loop() {
  if (!client.connected()) {
    reconnect();
  }
  client.loop();

  // Serial.println("Past client.loop()");
  
  int reading = digitalRead(buttonPin);
  // Serial.println("Button reading: " + String(reading));
  
  if (reading != lastButtonState) {
    lastDebounceTime = millis();
  }
  
  if ((millis() - lastDebounceTime) > debounceDelay) {
    if (reading != buttonState) {
      buttonState = reading;
      
      if (buttonState == HIGH) {
        unsigned long uptime = millis();
        
        String payload = "{\"uptime_ms\":" + String(uptime) + 
                        ",\"button\":\"pressed\",\"device\":\"ESP32\"}";
        
        Serial.print("Button pressed! ");
        Serial.println(payload);
        
        client.publish(mqtt_topic, payload.c_str());
      }
    }
  }
  
  lastButtonState = reading;
}