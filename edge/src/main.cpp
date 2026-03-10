#include "DHT.h"
#include <WiFi.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

#define DHTPIN 13     // 設定 DATA 接在 Pin 13 (D13)
#define DHTTYPE DHT11 // 定義感測器型號
DHT dht(DHTPIN, DHTTYPE);

// 這些常數由 PlatformIO 的 extra_script 在編譯時自動注入 (.env 檔案提供)
// WIFI_SSID
// WIFI_PASS
// BACKEND_IP

// 將 BACKEND_IP 轉換為 String 用於 URL，避免型別問題
String serverName = "http://" + String(BACKEND_IP) + ":8000/sensor-data";

void setup() {
  Serial.begin(9600);
  dht.begin();

  // 連接 WiFi
  WiFi.begin(WIFI_SSID, WIFI_PASS);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nConnected to WiFi network with IP Address: ");
  Serial.println(WiFi.localIP());
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
  Serial.print(" %\t");
  Serial.print("溫度: ");
  Serial.print(t);
  Serial.println(" *C");

  // 發送 HTTP POST 請求
  if(WiFi.status() == WL_CONNECTED){
    HTTPClient http;
    http.begin(serverName);
    http.addHeader("Content-Type", "application/json");

    // 使用 ArduinoJson v7 建立 JSON
    JsonDocument doc;
    doc["temperature"] = t;
    doc["humidity"] = h;
    String requestBody;
    serializeJson(doc, requestBody);

    int httpResponseCode = http.POST(requestBody);

    if (httpResponseCode > 0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
    } else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
  } else {
    Serial.println("WiFi Disconnected");
  }

  // 額外延遲避免發送過於頻繁 (總計約 12 秒一次)
  delay(10000);
}
