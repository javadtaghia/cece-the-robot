"""Produce review artifacts and payload sensitivity evidence from actual dynamics."""
import json,math
from pathlib import Path
import numpy as np
import mujoco
from PIL import Image,ImageDraw
import drive_study as s
import crank_drive as crank

def geometry_scad(m,d,path):
    lines=['// Physics-rig geometry at rest; dimensions mm. Not printable parts.','$fn=32;']
    for i in range(1,m.ngeom):
        col=m.geom_rgba[i];kind=m.geom_type[i];size=m.geom_size[i]*1000
        T=np.eye(4);T[:3,:3]=d.geom_xmat[i].reshape(3,3);T[:3,3]=d.geom_xpos[i]*1000
        lines += [f'// {m.geom(i).name}',f'color({col.tolist()}) multmatrix({T.tolist()})']
        if kind==mujoco.mjtGeom.mjGEOM_BOX:shape=f'cube({(size*2).tolist()},center=true);'
        elif kind==mujoco.mjtGeom.mjGEOM_CYLINDER:shape=f'cylinder(r={size[0]},h={2*size[1]},center=true);'
        elif kind==mujoco.mjtGeom.mjGEOM_CAPSULE:shape=f'hull(){{translate([0,0,{size[1]}])sphere({size[0]});translate([0,0,{-size[1]}])sphere({size[0]});}}'
        elif kind==mujoco.mjtGeom.mjGEOM_ELLIPSOID:shape=f'scale({size.tolist()})sphere(1);'
        elif kind==mujoco.mjtGeom.mjGEOM_MESH:
            mesh=m.geom_dataid[i];v0=m.mesh_vertadr[mesh];nv=m.mesh_vertnum[mesh];f0=m.mesh_faceadr[mesh];nf=m.mesh_facenum[mesh]
            shape=f'polyhedron(points={(m.mesh_vert[v0:v0+nv]*1000).tolist()},faces={m.mesh_face[f0:f0+nf].tolist()},convexity=10);'
        else:shape='sphere(1);'
        lines.append(shape)
    path.write_text('\n'.join(lines))

def outputs():
    c=json.loads((s.OUT/'recommended_research_config.json').read_text())
    sensitivity=[]
    for mass_asym in [False,True]:
        for shell in [False,True]:
            cc=c.copy();cc.update(realistic_hardware=mass_asym,single_shell=shell)
            r,_,_,_=s.run(cc,15);r['clearance']=s.clearance_audit(cc);sensitivity.append(r)
    (s.OUT/'payload_sensitivity.json').write_text(json.dumps(sensitivity,indent=2))
    # Select a passing environmental trial for the demonstration, explicitly label it.
    robust=json.loads((s.OUT/'robustness.json').read_text())[0]
    passing=[r for r in robust['cases'] if r['walking_screen_pass']]
    passing.sort(key=lambda r:r['travel_mm'][0],reverse=True)
    demo=json.loads((s.OUT/'audio_demo_config.json').read_text()) if (s.OUT/'audio_demo_config.json').exists() else (passing[0]['config'] if passing else c)
    (s.OUT/'demo_config.json').write_text(json.dumps(demo,indent=2))
    m,d=s.build(demo,s.OUT/'demo_hip.xml');geometry_scad(m,d,s.ROOT/'chick_drive_rig.scad')
    render=mujoco.Renderer(m,600,800);camera=mujoco.MjvCamera();camera.distance=.28;camera.azimuth=125;camera.elevation=-18
    frames=[];samples=[]
    for k in range(240):
        for _ in range(4):s.command(m,d,demo);mujoco.mj_step(m,d,nstep=10)
        camera.lookat[:]=d.subtree_com[m.body('assembly_A').id]+[0,0,.005]
        render.update_scene(d,camera=camera)
        if k%2==0:
            frame=Image.fromarray(render.render());draw=ImageDraw.Draw(frame)
            draw.rectangle((0,0,800,49),fill='white')
            draw.text((12,7),f'FREE-BASE physics: one DC hip | {d.time:.2f} s | research rig, not final chick',fill='black')
            draw.text((12,27),f'Demo: friction {demo["friction"]}, mass x{demo["mass_scale"]}, motor equivalent {demo["stall"]/.0363*3:.1f} V; nominal audio layout, drift unresolved',fill='black')
            frames.append(frame)
        samples.append([float(d.time),*d.subtree_com[m.body('assembly_A').id].tolist(),float(d.qpos[m.joint('hip').qposadr[0]]),float(d.actuator_force[0])])
    frames[0].save(s.OUT/'hip_drive.gif',save_all=True,append_images=frames[1:],duration=80,loop=0,optimize=True)
    frames[12].save(s.OUT/'hip_drive.png');render.close()
    (s.OUT/'demo_trace.json').write_text(json.dumps(samples))
    # Side-by-side mechanism photograph for crank study, actual free-base state.
    cc=json.loads((s.OUT/'crank_config.json').read_text());m,d=crank.build(cc,s.OUT/'crank_drive.xml')
    geometry_scad(m,d,s.ROOT/'chick_crank_rig.scad')
    render=mujoco.Renderer(m,600,800);camera=mujoco.MjvCamera();camera.lookat[:]=[0,0,.070];camera.distance=.34;camera.azimuth=125;camera.elevation=-20
    for _ in range(200):crank.command(m,d,cc);mujoco.mj_step(m,d,nstep=5)
    render.update_scene(d,camera=camera);Image.fromarray(render.render()).save(s.OUT/'crank_drive.png');render.close()
    # Text summary, retained alongside raw data to disclose demo selection.
    print(json.dumps({'demo_config':demo,'payload_sensitivity':[{'motor_asymmetry':x['config']['realistic_hardware'],'single_shell':x['config']['single_shell'],'upright':x['upright'],'travel_mm':x['travel_mm'],'max_tilt_deg':x['max_tilt_deg']} for x in sensitivity]},indent=2))

if __name__=='__main__':outputs()
