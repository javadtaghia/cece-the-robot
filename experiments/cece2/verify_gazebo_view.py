"""Observe joint motion in the live Cece 2 view, without claiming foot lift."""
from pathlib import Path
import json,math,threading,time
from gz.transport13 import Node
from gz.msgs10.model_pb2 import Model
HERE=Path(__file__).resolve().parent
rows=[];lock=threading.Lock()
def callback(msg):
    row={'position':[msg.pose.position.x,msg.pose.position.y,msg.pose.position.z],
         'joints':{j.name:j.axis1.position for j in msg.joint}}
    with lock:rows.append(row)
node=Node()
node.subscribe(Model,'/world/cece2_room/model/cece2/joint_state',callback)
time.sleep(12)
with lock:samples=list(rows)
if not samples:raise RuntimeError('No live Cece 2 state messages received')
names=('left_hip','left_ankle','right_hip','right_ankle')
report={'samples':len(samples),'observation_wall_seconds':12,
    'joint_motion_range_deg':{n:math.degrees(max(r['joints'].get(n,0) for r in samples)-min(r['joints'].get(n,0) for r in samples)) for n in names},
    'model_position_displacement_mm':[1000*(b-a) for a,b in zip(samples[0]['position'],samples[-1]['position'])],
    'scope':'Observed Gazebo joint/state messages; no foot-contact, lift-and-land or speed-ratio acceptance test'}
(HERE/'gazebo_view_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
