"""Exact printed mesh ankle sweep, no physics/contact proxies or servo."""
import sys,json,warnings
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cece_mesh_deps'))
import trimesh
warnings.filterwarnings('ignore',category=RuntimeWarning)
r=Path(__file__).resolve().parents[1];p=r/'xgoduck_project_repo/experiments/cece';out={}
for side,legfile,footfile,x in [('right','OttoDIY_Leg_V9.stl','cece_foot_right_clean.stl',25.5),('left','leg_mirror.stl','cece_foot_left_clean.stl',-25.5)]:
 leg=trimesh.load(p/'parts'/legfile,force='mesh');foot=trimesh.load(p/'parts_adafruit_draft'/footfile,force='mesh')
 vals={}
 for angle in range(-45,46,5):
  m=leg.copy();m.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(angle),[0,1,0],[x,0,-71.5]));inter=trimesh.boolean.intersection([m,foot],engine='manifold');vals[str(angle)]=round(abs(inter.volume),4)
 print(side,vals)
 out[side]={'leg':legfile,'foot':footfile,'axis_point_mm':[x,0,-71.5],'intersect_volume_mm3':vals}
out['limits']='Estimated axis; finite angle samples only; servo, horn, fasteners, forces, tolerances, assembly, body, other parts and walking omitted. Zero volume does not mean zero contact or positive clearance.'
(r/'otto_joint_review/cece_clean_foot_sweep.json').write_text(json.dumps(out,indent=2))
