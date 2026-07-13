#include <ESP8266WiFi.h>
#include <ESP8266WebServer.h>
#include "config.h"   // Define WIFI_SSID e WIFI_PASSWORD -- NUNCA commitado

ESP8266WebServer server(80);

float ultimaHumidade = -1;
float ultimaTemperatura = -1;
unsigned long ultimaAtualizacao = 0;
bool primeiraLeituraRecebida = false;

void handleRoot() {
  unsigned long segundosDesdeAtualizacao = primeiraLeituraRecebida
      ? (millis() - ultimaAtualizacao) / 1000
      : 0;

  String json = "{";
  json += "\"temperatura\":" + String(ultimaTemperatura, 1) + ",";
  json += "\"humidade\":" + String(ultimaHumidade, 1) + ",";
  json += "\"dados_validos\":" + String(primeiraLeituraRecebida ? "true" : "false") + ",";
  json += "\"segundos_desde_atualizacao\":" + String(segundosDesdeAtualizacao);
  json += "}";

  server.send(200, "application/json", json);
}

void setup() {
  // ATENCAO: mesma Serial usada para gravar/depurar via USB (CH340). Em
  // producao, o DIP switch deve estar na posicao "Mega2560+ESP8266"
  // (chaves 1 e 2 = ON) e o seletor RXD3/TXD3 na posicao correspondente.
  Serial.begin(9600); // Precisa bater com Serial3.begin(9600) do Mega

  WiFi.mode(WIFI_STA);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
  }

  server.on("/", handleRoot);
  server.begin();
}

void loop() {
  server.handleClient();

  if (Serial.available() > 0) {
    String linha = Serial.readStringUntil('\n');
    linha.trim();

    int virgula = linha.indexOf(',');
    if (virgula > 0) {
      float h = linha.substring(0, virgula).toFloat();
      float t = linha.substring(virgula + 1).toFloat();

      // Validacao de sanidade: protege contra lixo eventual no barramento serial.
      if (h > 0 && h <= 100 && t > -40 && t <= 80) {
        ultimaHumidade = h;
        ultimaTemperatura = t;
        ultimaAtualizacao = millis();
        primeiraLeituraRecebida = true;
      }
    }
  }
}
