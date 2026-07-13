#include <DHT.h>

#define DHTPIN 2        // Pino de dados do DHT11 (confirmado fisicamente ligado no pino 2)
#define DHTTYPE DHT11

DHT dht(DHTPIN, DHTTYPE);

unsigned long ultimaLeitura = 0;
const unsigned long INTERVALO_MS = 2000;  // DHT11 exige >=1s entre leituras; usamos 2s de folga

void setup() {
  Serial.begin(115200);   // Canal USB, so para debug (Monitor Serial da IDE)
  Serial3.begin(9600);    // Canal fisico para o ESP8266 (pinos TX3/RX3)
  dht.begin();

  Serial.println("Mega pronto. Lendo DHT11 e enviando via Serial3...");
}

void loop() {
  unsigned long agora = millis();

  if (agora - ultimaLeitura >= INTERVALO_MS) {
    ultimaLeitura = agora;

    float h = dht.readHumidity();
    float t = dht.readTemperature();

    // Descarta leituras invalidas do sensor (protocolo sensivel a tempo)
    if (isnan(h) || isnan(t)) {
      Serial.println("Falha na leitura do DHT11 (NaN). Pulando este ciclo.");
      return;
    }

    // Envia no formato limpo "H,T" -- sem texto, sem unidades.
    // O ESP8266 do outro lado so precisa dar split(',') e nao correr
    // risco de casar numeros de lixo de boot como aconteceu com o regex.
    Serial3.print(h, 1);
    Serial3.print(",");
    Serial3.println(t, 1);

    Serial.print("Enviado -> H: ");
    Serial.print(h);
    Serial.print("% | T: ");
    Serial.print(t);
    Serial.println(" C");
  }
}
