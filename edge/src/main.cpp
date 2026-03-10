#include "DHT.h"
#define DHTPIN 13     // 設定 DATA 接在 Pin 13 (D13)
#define DHTTYPE DHT11 // 定義感測器型號
DHT dht(DHTPIN, DHTTYPE);

void setup() {
  Serial.begin(9600);
  dht.begin();
}

void loop() {
  delay(2000); // DHT11 讀取頻率較慢，建議間隔 2 秒以上
  float h = dht.readHumidity(); // 讀取濕度
  float t = dht.readTemperature(); // 讀取攝氏溫度

  if (isnan(h) || isnan(t)) {
    Serial.println("讀取失敗!");
    return;
  }
  Serial.print("濕度: ");
  Serial.print(h);
  Serial.print(" %t\t");
  Serial.print("溫度: ");
  Serial.print(t);
  Serial.println(" *C");
}
