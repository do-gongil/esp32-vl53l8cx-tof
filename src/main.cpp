#include <Arduino.h>
#include <Wire.h>
#include <vl53l8cx.h>

#define SDA_PIN 8
#define SCL_PIN 9

// 시리얼 출력 형식 (프레임당 한 줄):
//   F,<d0>,<d1>,...,<d63>
// 인덱스 = y*8 + x, 단위 mm, 유효하지 않은 셀은 -1
// tools/tof_viewer.py 가 이 형식을 읽어 8x8 히트맵으로 표시한다.

VL53L8CX sensor(&Wire, -1, -1);   // LPn, I2C_RST 미사용

void setup() {
  Serial.begin(115200);
  delay(1000);
  Serial.println("# VL53L8CX start");

  Wire.begin(SDA_PIN, SCL_PIN);
  Wire.setClock(400000);

  sensor.begin();
  Serial.print("# init... ");
  if (sensor.init() != 0) {
    Serial.println("FAILED - check wiring");
    while (1) delay(1000);
  }
  Serial.println("OK");

  sensor.set_resolution(VL53L8CX_RESOLUTION_8X8);
  sensor.set_ranging_frequency_hz(15);
  sensor.start_ranging();
}

void loop() {
  VL53L8CX_ResultsData r;
  uint8_t ready = 0;
  sensor.check_data_ready(&ready);
  if (!ready) { delay(2); return; }

  sensor.get_ranging_data(&r);
  Serial.print('F');
  for (int zone = 0; zone < 64; zone++) {
    int i = zone * VL53L8CX_NB_TARGET_PER_ZONE;
    Serial.print(',');
    if (r.target_status[i] == 5)          // 5 = 유효 측정
      Serial.print(r.distance_mm[i]);
    else
      Serial.print(-1);
  }
  Serial.println();
}
