"""Ask Gazebo's own screenshot service to save the current 3D view."""
from pathlib import Path
import subprocess
HERE=Path(__file__).resolve().parent
subprocess.run(['gz','service','-s','/gui/screenshot','--reqtype','gz.msgs.StringMsg',
                '--reptype','gz.msgs.Boolean','--timeout','5000','--req',
                f'data: "{HERE}"'],check=True)
