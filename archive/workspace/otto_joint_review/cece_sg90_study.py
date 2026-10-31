"""Cece ankle first-pass SG90 geometric interference study (NOT final design)."""
import sys,json,warnings
from pathlib import Path
import numpy as np
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'cece_mesh_deps'))
import trimesh
from PIL import Image,ImageDraw,ImageFont
warnings.filterwarnings('ignore',category=RuntimeWarning)
root=Path(__file__).resolve().parents[1];out=Path(__file__).resolve().parent
p=root/'xgoduck_project_repo/experiments/cece/parts'
leg=trimesh.load(p/'OttoDIY_Leg_V9.stl',force='mesh');foot=trimesh.load(p/'OttoDIY_foot_V9.stl',force='mesh')
pivot=[25.5,0,-71.5]
# Assumptions: overall retailer dimensions do not describe the separate shell,
# turret, output-spline offset or horn. Generic proxies, NOT measured hardware.
body=trimesh.creation.box(extents=[12.2,22,23]);body.apply_translation([25.5,-4,-67])
turret=trimesh.creation.cylinder(radius=6.1,height=3.25,sections=40)
turret.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));turret.apply_translation([25.5,-16.625,-71.5])
horn=trimesh.creation.cylinder(radius=4,height=3.75,sections=40)
horn.apply_transform(trimesh.transformations.rotation_matrix(np.pi/2,[1,0,0]));horn.apply_translation([25.5,-20.125,-71.5])
def volume(a,b):return round(abs(trimesh.boolean.intersection([a,b],engine='manifold').volume),3)
results={'status':'INCONCLUSIVE; ASSUMED SG90 SHAPES; NOT PRINT VALIDATION','source_dimensions_mm':[23,12.2,29],'assumptions':'Body, shaft, turret and horn geometry/placement are provisional and do not represent verified purchased components. Screw not modelled. Proxy horn is a cylinder, not supplier horn. Estimate pivot only.','neutral_overlap_mm3':{'body_vs_leg':volume(body,leg),'body_vs_foot':volume(body,foot),'turret_vs_leg':volume(turret,leg),'horn_vs_foot':volume(horn,foot)},'angles':{}}
for a in range(-20,21,5):
 transform=trimesh.transformations.rotation_matrix(np.deg2rad(a),[0,1,0],pivot)
 l=leg.copy();l.apply_transform(transform);s=body.copy();s.apply_transform(transform);t=turret.copy();t.apply_transform(transform)
 results['angles'][str(a)]={'leg_vs_foot':volume(l,foot),'body_vs_foot':volume(s,foot),'turret_vs_foot':volume(t,foot)}
(out/'cece_sg90_proxy_results.json').write_text(json.dumps(results,indent=2))
print(json.dumps(results,indent=2))
font=ImageFont.truetype('C:/Windows/Fonts/arial.ttf',18)
u=np.array([.82,.57,0]);v=np.array([-.25,.36,.9]);u/=np.linalg.norm(u);v/=np.linalg.norm(v);dep=np.cross(u,v)
def frame(angle):
 tr=trimesh.transformations.rotation_matrix(np.deg2rad(angle),[0,1,0],pivot)
 objects=[(foot,(56,135,200)),(leg,(241,153,57)),(body,(128,78,177)),(turret,(202,62,64)),(horn,(120,120,120))]
 img=Image.new('RGB',(900,700),'#f8fbfd');d=ImageDraw.Draw(img)
 d.text((20,17),'Cece ankle: exploratory SG90 proxy, not a fit confirmation',font=font,fill='#172737')
 d.text((20,45),f'Angle {angle:+.0f} deg | blue foot | orange leg | purple motor | red turret',font=font,fill='#172737')
 triangles=[];center=np.array([30,0,-65])
 for n,(mesh,col) in enumerate(objects):
  m=mesh.copy()
  if n in (1,2,3):m.apply_transform(tr)
  for tri in m.triangles:
   t=tri-center;xy=np.column_stack((t@u,t@v))*6.6;xy[:,0]+=450;xy[:,1]=350-xy[:,1]
   normal=np.cross(t[1]-t[0],t[2]-t[0]);ln=np.linalg.norm(normal);shade=.72+.28*abs(float(normal@np.array([.4,-.6,.7]))/ln) if ln else .72
   triangles.append((float((t@dep).mean()),xy,tuple(int(c*shade) for c in col)))
 for _,xy,col in sorted(triangles,key=lambda x:x[0]):d.polygon([tuple(x) for x in xy],fill=col)
 d.rounded_rectangle((16,575,884,676),radius=8,fill='#fff0db')
 d.text((28,588),'Proxy geometry is assumed. Neutral turret intersects leg; horn intersects foot.',font=font,fill='#552600')
 d.text((28,617),'Screw, exact horn and purchased servo dimensions not verified.',font=font,fill='#552600')
 d.text((28,646),'Do not use this to authorize printing or powered operation.',font=font,fill='#552600')
 return img
angles=list(range(-20,21,4))+list(range(16,-21,-4));frames=[frame(a) for a in angles];frames[5].save(out/'cece_sg90_proxy_neutral.png');frames[0].save(out/'cece_sg90_proxy_motion.gif',save_all=True,append_images=frames[1:],duration=120,loop=0,optimize=True)
