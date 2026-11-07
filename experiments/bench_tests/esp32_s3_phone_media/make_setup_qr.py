"""Read setup Wi-Fi details from the physical ESP and create a local Wi-Fi QR code.
The generated credential QR stays in ignored captures/, not in Git.
"""
import argparse
import json
from pathlib import Path
import time

import qrcode
import serial

parser = argparse.ArgumentParser()
parser.add_argument("--port", default="COM4")
args = parser.parse_args()
values = {}
with serial.Serial(args.port, 115200, timeout=1) as port:
    port.reset_input_buffer()
    port.write(b"i\n")
    deadline = time.monotonic() + 8
    while time.monotonic() < deadline:
        line = port.readline().decode("utf-8", errors="replace").strip()
        if line.startswith(("SETUP_SSID ", "SETUP_PASSWORD ", "SETUP_URL ")):
            key, value = line.split(" ", 1)
            values[key] = value
        if len(values) == 3:
            break
if len(values) != 3:
    raise SystemExit("ESP setup details not received; close Serial Monitor and try again.")

def escape(value):
    for symbol in ('\\', ';', ',', ':', '"'):
        value = value.replace(symbol, '\\' + symbol)
    return value

payload = "WIFI:T:WPA;S:" + escape(values["SETUP_SSID"]) + ";P:" + escape(values["SETUP_PASSWORD"]) + ";;"
output = Path(__file__).resolve().parent / "captures"
output.mkdir(exist_ok=True)
qr = qrcode.QRCode(box_size=9, border=4)
qr.add_data(payload)
qr.make(fit=True)
qr.make_image(fill_color="black", back_color="white").save(output / "setup_wifi_qr.png")
(output / "setup_details.json").write_text(json.dumps(values, indent=2) + "\n", encoding="utf-8")
print("Setup Wi-Fi:", values["SETUP_SSID"])
print("Setup page:", values["SETUP_URL"])
print("QR code:", output / "setup_wifi_qr.png")
