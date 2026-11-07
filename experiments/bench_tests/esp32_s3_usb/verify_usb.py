"""Read the physical ESP32 serial port and save the observed hello-world output."""
import argparse
import datetime
import json
from pathlib import Path
import time

import serial

parser = argparse.ArgumentParser()
parser.add_argument("--port", default="COM4")
args = parser.parse_args()
expected = "Hello world! Cece ESP32-S3 is running."
lines = []
with serial.Serial(args.port, 115200, timeout=1) as port:
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        line = port.readline().decode("utf-8", errors="replace").strip()
        if line:
            lines.append(line)
            print(line, flush=True)

matches = lines.count(expected)
result = {
    "checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "port": args.port,
    "baud": 115200,
    "board": "Seeed XIAO ESP32-S3 / Sense",
    "fqbn": "esp32:esp32:XIAO_ESP32S3:USBMode=hwcdc,CDCOnBoot=default,PSRAM=opi",
    "expected_line": expected,
    "matching_lines": matches,
    "observed_lines": lines,
    "passed": matches >= 3,
    "scope": "Physical board USB serial hello world",
}
Path(__file__).with_name("usb_verification.json").write_text(
    json.dumps(result, indent=2) + "\n", encoding="utf-8"
)
if not result["passed"]:
    raise SystemExit("FAIL: fewer than three hello-world messages received")
print(f"PASS: {matches} hello-world messages received from the physical board.")
