"""Focus and follow Cece 2 using Gazebo's camera services."""
import subprocess
def request(service,kind,text):
    subprocess.run(['gz','service','-s',service,'--reqtype',kind,
                    '--reptype','gz.msgs.Boolean','--timeout','5000','--req',text],check=True)
request('/gui/follow','gz.msgs.StringMsg','data: "cece2"')
request('/gui/follow/offset','gz.msgs.Vector3d','x: 0.15 y: -0.20 z: 0.10')
