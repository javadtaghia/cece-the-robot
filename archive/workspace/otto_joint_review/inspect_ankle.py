"""Inspect one original Otto V9 ankle. Pivot is estimated, servo omitted."""
import sys, zipfile, xml.etree.ElementTree as ET, json, warnings
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]/'cece_mesh_deps'))
import numpy as np
import trimesh
from PIL import Image, ImageDraw, ImageFont
warnings.filterwarnings('ignore', category=RuntimeWarning)
root=Path(__file__).resolve().parents[1]; out=Path(__file__).resolve().parent
leg=trimesh.load(root/'otto_reference/3Dprint/OttoDIY_Leg_V9.stl',force='mesh')
foot=trimesh.load(root/'otto_reference/3Dprint/OttoDIY_foot_V9.stl',force='mesh')
# Meshes share original author coordinates. Axis estimated visually from the side-hole.
pivot=[25.5,0,-71.5]
volumes={}
for deg in range(-20,21,5):
    moved=leg.copy(); moved.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(deg),[0,1,0],pivot))
    overlap=trimesh.boolean.intersection([moved,foot],engine='manifold')
    volumes[str(deg)]=float(abs(overlap.volume))
# Compare unique vertex clouds after translation only: printing changes origin.
ns={'m':'http://schemas.microsoft.com/3dmanufacturing/core/2015/02'}
with zipfile.ZipFile(root/'Otto_Simple_Print/Otto_Simple_PLA_H2S.3mf') as z:
    for nm,obj,mesh in [('leg',3,leg),('foot',4,foot)]:
        doc=ET.fromstring(z.read(f'3D/Objects/object_{obj}.model'))
        vertices=np.array([[float(v.attrib[q]) for q in 'xyz'] for v in doc.findall('.//m:vertex',ns)])
        def canonical(v):
            v=np.round(v-v.min(axis=0),4); return np.unique(v,axis=0)
        av=canonical(vertices); bv=canonical(mesh.vertices)
        print(nm,'3mf stl match',av.shape==bv.shape and np.allclose(av,bv,atol=.001), '3mf',av.shape,'stl',bv.shape)
print('mesh intersection cubic mm:',volumes)
fontpath='C:/Windows/Fonts/arial.ttf'
font=ImageFont.truetype(fontpath,21); small=ImageFont.truetype(fontpath,16)
u=np.array([.82,.57,0.]);v=np.array([-.25,.36,.9]);u/=np.linalg.norm(u);v/=np.linalg.norm(v);dep=np.cross(u,v)
def frame(deg):
    moved=leg.copy();moved.apply_transform(trimesh.transformations.rotation_matrix(np.deg2rad(deg),[0,1,0],pivot))
    img=Image.new('RGB',(860,680),'#f9fbfd'); d=ImageDraw.Draw(img)
    d.text((28,20),'Otto V9: one ankle, original printed meshes',font=font,fill='#172737')
    d.text((28,51),f'Leg angle: {deg:+.0f} degrees   |   Blue: foot   Orange: leg',font=small,fill='#263e53')
    tris=[]; center=np.array([30.,0.,-65.])
    for mesh,color in [(foot,(64,137,202)),(moved,(245,155,56))]:
        for tri in mesh.triangles:
            t=tri-center; normal=np.cross(t[1]-t[0],t[2]-t[0]); n=np.linalg.norm(normal)
            shade=.72+.28*abs(float(normal@np.array([.4,-.6,.7]))/n) if n else .72
            xy=np.column_stack((t@u,t@v))*7.1
            xy[:,0]+=430;xy[:,1]=350-xy[:,1]
            tris.append((float((t@dep).mean()),xy,tuple(int(x*shade) for x in color)))
    for _,xy,col in sorted(tris,key=lambda x:x[0]):d.polygon([tuple(p) for p in xy],fill=col)
    d.rounded_rectangle((20,567,840,654),radius=8,fill='#e5eef5')
    d.text((35,578),'Illustrative motion: estimated pivot; servo and screws not shown.',font=small,fill='#172737')
    d.text((35,603),'Does not prove a secure connection or fit of your physical parts.',font=small,fill='#172737')
    return img
angles=list(range(-20,21,2))+list(range(18,-21,-2))
frames=[frame(a) for a in angles]
frames[10].save(out/'otto_ankle_neutral.png')
frames[0].save(out/'otto_ankle_motion.gif',save_all=True,append_images=frames[1:],duration=90,loop=0,optimize=True)
(out/'collision_results.json').write_text(json.dumps({'pivot_estimate_mm':pivot,'axis':'Y','overlap_mm3_by_degrees':volumes,'limitations':'Servo, horn, screws, print tolerances, physical forces and other joints are excluded.'},indent=2))
