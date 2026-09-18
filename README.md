# vl53l8cx-tof

VL53L8CX 8×8 Time-of-Flight 센서를 ESP32-S3 에서 구동하고, 측정값을 시리얼로 흘려
PC 에서 실시간 히트맵으로 확인하는 펌웨어입니다.

## Hardware

| 항목 | 값 |
|---|---|
| 보드 | ESP32-S3-DevKitC-1 (PlatformIO 환경 `yd_esp32_s3`) |
| 메모리 | 16 MB flash, PSRAM `qio_opi` (N16R8) |
| 센서 | STMicroelectronics VL53L8CX (8×8 multizone ToF) |
| 버스 | I2C — SDA `GPIO8`, SCL `GPIO9`, 400 kHz |
| 시리얼 | 115200 baud (업로드 921600) |

센서는 LPn / I2C_RST 핀을 쓰지 않고 `VL53L8CX sensor(&Wire, -1, -1)` 로 초기화합니다.

같은 장비 구성에 함께 쓴 부품: Arducam 1080P WDR USB 카메라 + M12 1.95 mm 렌즈, ADS1115 ADC.

## Wire protocol

펌웨어는 프레임마다 한 줄을 내보냅니다.

```
F,<d0>,<d1>,...,<d63>
```

- 인덱스 = `y*8 + x`
- 단위 mm
- `target_status != 5` 인 셀은 `-1` (무효)
- 15 Hz

`#` 로 시작하는 줄은 상태 메시지입니다.

## Build / Flash

```bash
pio run -t upload
pio device monitor -b 115200
```

## Viewer

```bash
pip install -r tools/requirements.txt
python tools/tof_viewer.py              # USB 시리얼 포트 자동 탐지
python tools/tof_viewer.py COM7         # 포트 지정
python tools/tof_viewer.py COM7 --max 2000   # 색상 범위 상한 (mm)
```

뷰어는 수신 버퍼에 쌓인 줄을 모두 읽고 **마지막 유효 프레임만** 그립니다.
그리기가 수신보다 느려도 지연이 누적되지 않습니다.

## Dependencies

`stm32duino/STM32duino VL53L8CX` 는 `platformio.ini` 의 `lib_deps` 로 빌드 시 내려받습니다.
이 저장소에 vendoring 하지 않습니다.

## 관련 프로젝트

이 펌웨어를 확장해 **RGB 카메라와 동축으로 융합**한 프로젝트가 있습니다 —
빔스플리터로 광축을 겹쳐 영상의 특정 지점 depth 를 읽습니다:
**[vl53l8cx-rgb-fusion](https://github.com/do-gongil/vl53l8cx-rgb-fusion)**

그쪽 펌웨어는 카메라 프레임과 짝을 맞추기 위해 타임스탬프 · `target_status` 원본 ·
ping · LED 펄스가 추가된 프로토콜 v2 를 씁니다. 센서 하나만 돌려보는 것이 목적이라면
이 저장소가 더 간단합니다.

## License

MIT — `LICENSE` 참조.
