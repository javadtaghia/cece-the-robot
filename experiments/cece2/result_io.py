"""Read newly generated reports, or preserved reports from the compact archive."""
from pathlib import Path
import json,zipfile
HERE=Path(__file__).resolve().parent
def result_bytes(name):
    filename=f'bullet_{name}_results.json'
    local=HERE/'results'/filename
    if local.exists():return local.read_bytes()
    with zipfile.ZipFile(HERE/'raw_simulation_results.zip') as archive:
        return archive.read(filename)
def load_result(name):return json.loads(result_bytes(name))
