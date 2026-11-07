"""Check actual Sense camera and microphone through USB, without Wi-Fi credentials.

Images/audio remain in ignored captures/. The JSON report contains measurements only.
Close Arduino Serial Monitor before running this script.
"""
import argparse
import array
import datetime
import io
import json
from pathlib import Path
import sys
import time
import wave

from PIL import Image
import serial

parser = argparse.ArgumentParser()
parser.add_argument("--port", default="COM4")
parser.add_argument("--output-dir", type=Path, help="Directory for captures and the verification report")
args = parser.parse_args()
root = args.output_dir.resolve() if args.output_dir else Path(__file__).resolve().parent
captures = root / "captures"
captures.mkdir(exist_ok=True)
report = {"checked_at_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
          "port": args.port, "camera_passed": False, "microphone_data_passed": False,
          "phone_wifi_playback_tested": False}

def wait_line(port, prefix, timeout=8):
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        line = port.readline().decode("utf-8", errors="replace").strip()
        if line.startswith(prefix):
            return line
        if line.startswith(("JPEG_ERROR", "PCM_ERROR")):
            raise RuntimeError(line)
    raise TimeoutError("No response for " + prefix)

def read_payload(port, command, prefix, maximum):
    port.reset_input_buffer()
    port.write(command.encode())
    line = wait_line(port, prefix + " ")
    length = int(line.split()[1])
    if not 0 < length <= maximum:
        raise RuntimeError("Invalid payload length: " + str(length))
    data = bytearray()
    deadline = time.monotonic() + 12
    while len(data) < length and time.monotonic() < deadline:
        data.extend(port.read(length - len(data)))
    if len(data) != length:
        raise RuntimeError(f"Short payload: {len(data)}/{length}")
    return bytes(data)

with serial.Serial(args.port, 115200, timeout=1) as port:
    time.sleep(0.25)
    port.reset_input_buffer()
    port.write(b"i\n")
    report["status"] = wait_line(port, "STATUS ")
    print(report["status"])
    try:
        jpeg = read_payload(port, "c", "JPEG", 1024 * 1024)
        image = Image.open(io.BytesIO(jpeg))
        image.load()
        report["camera"] = {"width": image.width, "height": image.height,
                            "jpeg_bytes": len(jpeg), "format": image.format}
        report["camera_passed"] = image.format == "JPEG" and image.width > 0 and image.height > 0
        (captures / "camera.jpg").write_bytes(jpeg)
        print("CAMERA", report["camera"])
    except Exception as error:
        report["camera_error"] = str(error)
        print("CAMERA", error)
    try:
        pcm = read_payload(port, "a", "PCM", 16000 * 2)
        samples = array.array("h", pcm)
        if sys.byteorder != "little":
            samples.byteswap()
        mean = sum(samples) / len(samples)
        rms = (sum((value - mean) ** 2 for value in samples) / len(samples)) ** 0.5
        peak = max(abs(value) for value in samples)
        report["microphone"] = {"sample_rate": 16000, "samples": len(samples),
            "peak": peak, "rms_without_dc": round(rms, 3),
            "nonzero_samples": sum(value != 0 for value in samples)}
        report["microphone_data_passed"] = len(samples) == 16000 and rms > 0
        with wave.open(str(captures / "microphone.wav"), "wb") as wav:
            wav.setnchannels(1)
            wav.setsampwidth(2)
            wav.setframerate(16000)
            wav.writeframes(pcm)
        print("MICROPHONE", report["microphone"])
    except Exception as error:
        report["microphone_error"] = str(error)
        print("MICROPHONE", error)

(root / "hardware_verification.json").write_text(json.dumps(report, indent=2) + "\n", encoding="utf-8")
if not (report["camera_passed"] and report["microphone_data_passed"]):
    raise SystemExit("Hardware check incomplete; see hardware_verification.json")
print("PASS: real camera JPEG and nonconstant microphone samples received over USB.")
