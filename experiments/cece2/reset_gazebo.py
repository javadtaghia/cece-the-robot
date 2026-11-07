"""Reset the separate Cece 2 Gazebo scene and resume physics."""
import subprocess
subprocess.run(['gz','service','-s','/world/cece2_room/control',
                '--reqtype','gz.msgs.WorldControl','--reptype','gz.msgs.Boolean',
                '--timeout','5000','--req','reset: {all: true} pause: false'],check=True)
