"""VL53L8CX 8x8 거리 히트맵 뷰어.

펌웨어가 보내는 'F,d0,...,d63' 줄을 읽어 각 셀에 거리(mm)를 표시한다.

사용법:
    python tools/tof_viewer.py            # 포트 자동 탐지 (CH343 등 USB 시리얼)
    python tools/tof_viewer.py COM7       # 포트 지정
    python tools/tof_viewer.py COM7 --max 2000   # 색상 범위 상한 (mm)
"""
import argparse
import sys

import matplotlib.pyplot as plt
import numpy as np
import serial
from serial.tools import list_ports

GRID = 8
BAUD = 115200


def find_port() -> str:
    usb_ports = [p.device for p in list_ports.comports() if p.vid is not None]
    if not usb_ports:
        sys.exit("USB 시리얼 포트를 찾지 못했습니다. 포트를 인자로 지정하세요.")
    return usb_ports[0]


def parse_frame(line: str) -> np.ndarray | None:
    if not line.startswith("F,"):
        return None
    parts = line.split(",")[1:]
    if len(parts) != GRID * GRID:
        return None
    try:
        values = np.array([int(v) for v in parts], dtype=float)
    except ValueError:
        return None
    values[values < 0] = np.nan          # 무효 셀
    return values.reshape(GRID, GRID)


def read_latest_frame(ser: serial.Serial) -> np.ndarray | None:
    """수신 버퍼에 쌓인 줄을 모두 읽고 마지막 유효 프레임만 돌려준다.

    그리기가 수신보다 느려도 오래된 프레임을 건너뛰므로 지연이 쌓이지 않는다.
    상태 메시지('#')는 순서대로 콘솔에 출력한다.
    """
    latest = None
    while True:
        line = ser.readline().decode(errors="ignore").strip()
        if line.startswith("#"):
            print(line)
        else:
            frame = parse_frame(line)
            if frame is not None:
                latest = frame
        if ser.in_waiting == 0:          # 버퍼를 다 비웠으면 종료
            return latest


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("port", nargs="?", help="시리얼 포트 (예: COM7)")
    ap.add_argument("--max", type=int, default=1500, help="색상 범위 상한 mm")
    args = ap.parse_args()

    port = args.port or find_port()
    ser = serial.Serial(port, BAUD, timeout=1)
    print(f"연결: {port} @ {BAUD}  (창을 닫으면 종료)")

    cmap = plt.get_cmap("viridis_r").copy()
    cmap.set_bad(color="#444444")        # NaN 셀은 회색

    plt.ion()
    fig, ax = plt.subplots(figsize=(6, 6))
    frame = np.full((GRID, GRID), np.nan)
    img = ax.imshow(frame, cmap=cmap, vmin=0, vmax=args.max)
    fig.colorbar(img, ax=ax, label="distance (mm)")
    ax.set_title("VL53L8CX")
    ax.set_xticks(range(GRID))
    ax.set_yticks(range(GRID))
    texts = [
        [ax.text(x, y, "", ha="center", va="center", color="white", fontsize=9)
         for x in range(GRID)]
        for y in range(GRID)
    ]

    while plt.fignum_exists(fig.number):
        frame = read_latest_frame(ser)
        if frame is None:
            plt.pause(0.001)
            continue
        frame = np.fliplr(frame)          # 좌우 반전 (센서 장착 방향 보정)
        img.set_data(frame)
        for y in range(GRID):
            for x in range(GRID):
                v = frame[y, x]
                texts[y][x].set_text("-" if np.isnan(v) else f"{int(v)}")
        fig.canvas.draw_idle()
        plt.pause(0.001)

    ser.close()


if __name__ == "__main__":
    main()
