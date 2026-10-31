"""Free-base single-hip investigation. Masses and motor ratings are hypotheses.
No imposed torso motion or position actuator. Coordinates: forward X, lateral Y.
"""
from pathlib import Path
import argparse, json, math, time
import xml.etree.ElementTree as E
import numpy as np
import mujoco
from chick_sim import add,vec

ROOT=Path(__file__).resolve().parent
OUT=ROOT/'out'/'drive_study'
OUT.mkdir(parents=True,exist_ok=True)
DEFAULT=dict(radius=.055,hip=.075,rear=.008,gap=.032,foot_length=.060,foot_width=.025,
             battery_z=.030,battery_y=.023,frequency=2.0,duty=.4,limit_deg=16.,
             stall=.0363,no_load=6.807,mass_scale=1.,friction=.65,layout='outboard')

def sole(c):
    r=c['radius']; n=10; vertices=[]
    # Hollow-looking sole is represented by convex solid collision mesh with
    # manually estimated printed mass; no density-based solid-foot mass.
    for top in [False,True]:
        for i in range(n+1):
            for j in range(n+1):
                x=c['foot_length']*(i/n-.5); y=c['foot_width']*(j/n-.5)
                z=r-math.sqrt(r*r-x*x-y*y)
                vertices.append((x,y,.014 if top else z))
    # MuJoCo uses convex hull for collision; shell rendering also uses hull here.
    points=np.array(vertices)
    faces=[];offset=(n+1)**2
    for i in range(n):
        for j in range(n):
            a=i*(n+1)+j;b=a+1;cc=a+n+1;d=cc+1
            faces.extend([(a,cc,b),(b,cc,d),(a+offset,b+offset,cc+offset),(b+offset,d+offset,cc+offset)])
    for edge in [[j for j in range(n+1)],[n*(n+1)+j for j in range(n+1)],
                 [i*(n+1) for i in range(n+1)],[i*(n+1)+n for i in range(n+1)]]:
        for a,b in zip(edge,edge[1:]):faces.extend([(a,b,a+offset),(b,b+offset,a+offset)])
    centre=points.mean(axis=0);oriented=[]
    for a,b,d in faces:
        if np.dot(np.cross(points[b]-points[a],points[d]-points[a]),(points[a]+points[b]+points[d])/3-centre)<0:b,d=d,b
        oriented.append((a,b,d))
    faces=oriented
    return points,faces

def build(c,save=None):
    root=E.Element('mujoco',model='CeCe corrected single-hip research rig')
    add(root,'compiler',angle='radian',inertiafromgeom='true')
    add(root,'option',timestep=c.get('timestep',.001),integrator='implicitfast',iterations='60')
    visual=add(root,'visual');add(visual,'global',offwidth='1000',offheight='800');add(visual,'headlight',ambient='.7 .7 .7',diffuse='.7 .7 .7')
    default=add(root,'default');add(default,'geom',friction=f'{c["friction"]} .001 .00002',solref='.006 1',condim='4')
    asset=add(root,'asset');v,f=sole(c)
    add(asset,'texture',name='floor_grid',type='2d',builtin='checker',rgb1='.82 .85 .87',rgb2='.65 .7 .73',width='128',height='128')
    add(asset,'material',name='grid',texture='floor_grid',texrepeat='20 20',texuniform='true')
    add(asset,'mesh',name='rocker',vertex=vec(v.flat),face=' '.join(str(i) for tri in f for i in tri))
    world=add(root,'worldbody');add(world,'light',pos='0 -1 2')
    add(world,'geom',name='floor',type='plane',size='3 3 .01',material='grid')
    base=add(world,'body',name='assembly_A',pos=f'{-c["rear"]} 0 {c["hip"]+.0004}')
    add(base,'freejoint',name='root')
    def geom(body,name,mass,**kw):
        return add(body,'geom',name=name,mass=mass*c['mass_scale'],**kw)
    for sign in [-1,1]:
        b=base if sign==-1 else add(base,'body',name='assembly_B')
        if sign==1:add(b,'joint',name='hip',axis='0 1 0',range=vec(np.radians([-c['limit_deg'],c['limit_deg']])),damping='.00012',frictionloss='.00008',armature='.000002')
        y=sign*c['gap']/2
        geom(b,f'foot_{sign}',.007,type='mesh',mesh='rocker',pos=vec([c['rear'],y,-c['hip']]),rgba='1 .46 .04 1')
        geom(b,f'leg_{sign}',.004,type='capsule',fromto=vec([0,y,0,c['rear'],y,-c['hip']+.012]),size='.0025',rgba='.8 .6 .15 1')
        # Opposing arm puts one cell near the other leg, as a yaw counterweight.
        by=(-sign if c.get('layout')=='crossed' else sign)*c['battery_y']; bz=c['battery_z']-c['hip']
        geom(b,f'arm_{sign}',.003,type='capsule',fromto=vec([0,y,-.010,c['rear'],by,bz]),size='.002',rgba='.4 .45 .5 1')
        geom(b,f'AA_{sign}',.024,type='cylinder',pos=vec([c['rear'],by,bz]),size='.00725 .02525',euler='0 1.570796 0',rgba='.65 .7 .75 1',contype='0',conaffinity='0')
        geom(b,f'holder_{sign}',.002,type='box',pos=vec([c['rear'],by,bz-.008]),size='.028 .009 .001',rgba='.2 .23 .25 1',contype='0',conaffinity='0')
        geom(b,f'board_{sign}',.004,type='box',pos=vec([c['rear'],by,bz+.012]),size='.014 .009 .003',rgba='.1 .55 .3 1',contype='0',conaffinity='0')
        # Hip hardware, motor on one side and balancing electronics on the other.
        hardware_mass=(.010 if sign==-1 else .002) if c.get('realistic_hardware') else .006
        geom(b,f'hip_hardware_{sign}',hardware_mass,type='box',pos=vec([0,sign*.007,0]),size='.006 .006 .005',rgba='.55 .6 .65 1',contype='0',conaffinity='0')
        # Split upper mass accounts for shell/audio load, not a rigid bridge.
        payload_mass=(.016 if sign==-1 else 0) if c.get('single_shell') else .008
        if c.get('audio_low'):payload_mass=.005 if sign==-1 else 0
        geom(b,f'upper_payload_{sign}',payload_mass,type='box',pos=vec([c['rear']+.003,sign*.009,.019]),size='.015 .007 .016',rgba='1 .8 .2 .35',group='1',contype='0',conaffinity='0')
        if c.get('audio_low') and sign==1:
            geom(b,'speaker_and_electronics_counterbalance',.011,type='box',pos=vec([c['rear']+.004,by,c['battery_z']-c['hip']+.023]),size='.015 .006 .010',rgba='.2 .4 .5 1',contype='0',conaffinity='0')
    # Separate collision bits let feet hit floor, but not virtual connecting rods.
    # Audit rods and AA envelopes geometrically in a separate full-cycle check.
    for g in root.findall('.//geom'):
        if g.attrib.get('name','').startswith(('leg_','arm_')):g.set('contype','0');g.set('conaffinity','0')
    act=add(root,'actuator');add(act,'general',name='DC_hip',joint='hip',gear='1',gainprm=vec([c['stall']]),
        biastype='affine',biasprm=vec([0,0,-c['stall']/c['no_load']]),ctrlrange='-1 1',ctrllimited='true',
        forcerange=f'-{c["stall"]} {c["stall"]}',forcelimited='true')
    xml=E.tostring(root,encoding='unicode')
    if save:Path(save).write_text(xml)
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m);mujoco.mj_forward(m,d)
    return m,d

def command(m,d,c):
    j=m.joint('hip');speed=d.qvel[j.dofadr[0]]
    # Signed DC duty and back EMF: permits braking, unlike the earlier cap model.
    duty=c['duty']*(1 if math.sin(2*math.pi*c['frequency']*max(0,d.time-.4))>=0 else -1) if d.time>.4 else 0
    if d.time>.4:duty=float(np.clip(duty+c.get('bias',0),-1,1))
    if c.get('heading_gain') and d.time>1:
        R=d.xmat[m.body('assembly_A').id].reshape(3,3)
        yaw=math.atan2(R[1,0],R[0,0])
        duty=float(np.clip(duty+np.clip(c['heading_gain']*yaw,-.12,.12),-1,1))
    d.ctrl[0]=duty
    return duty

def clearance_audit(c):
    m,d=build(c);qadr=m.joint('hip').qposadr[0];pairs={};minimum=.02
    aa=[i for i in range(m.ngeom) if m.geom_bodyid[i]==m.body('assembly_A').id]
    bb=[i for i in range(m.ngeom) if m.geom_bodyid[i]==m.body('assembly_B').id]
    for q in np.linspace(-np.radians(c['limit_deg']),np.radians(c['limit_deg']),81):
        d.qpos[qadr]=q;mujoco.mj_forward(m,d)
        for a in aa:
            for b in bb:
                dist=mujoco.mj_geomDistance(m,d,a,b,.02,None);minimum=min(minimum,dist)
                if dist<-.0001:
                    key=m.geom(a).name+' / '+m.geom(b).name
                    pairs[key]=min(pairs.get(key,0),round(float(dist*1000),3))
    return dict(sampled_poses=81,worst_separation_mm=round(float(minimum*1000),3),
                overlapping_envelopes_mm=pairs,pass_no_interpenetration=not pairs)

def run(c,seconds=6,trace=False):
    m,d=build(c);j=m.joint('hip');qadr=j.qposadr[0];vadr=j.dofadr[0]
    com0=d.subtree_com[m.body('assembly_A').id].copy()
    max_tilt=0;forces=[];single=[0,0];alternations=0;last=0;motion=[];toe=[];stop_time=0;pending=0;dwell=0
    fallen=False;stalled=0
    max_clearance=[0.,0.];slips=[]
    for i in range(int(seconds/.005)):
        duty=command(m,d,c);mujoco.mj_step(m,d,nstep=round(.005/m.opt.timestep))
        R=d.xmat[m.body('assembly_A').id].reshape(3,3)
        tilt=math.degrees(math.acos(np.clip(R[2,2],-1,1)));max_tilt=max(max_tilt,tilt)
        forces.append(abs(d.actuator_force[0]))
        if abs(math.degrees(d.qpos[qadr]))>c['limit_deg']-.5:stop_time+=.005
        if abs(duty)>.1 and abs(d.qvel[vadr])<.1:stalled+=.005
        contact=[False,False]
        for con in d.contact:
            a=m.geom(con.geom1).name;b=m.geom(con.geom2).name
            if 'floor' not in [a,b]:continue
            other=b if a=='floor' else a
            if other=='foot_-1':contact[0]=True
            elif other=='foot_1':contact[1]=True
            else:fallen=True
            if i%4==0 and other.startswith('foot_'):
                gid=m.geom(other).id;velocity=np.zeros(6)
                mujoco.mj_objectVelocity(m,d,mujoco.mjtObj.mjOBJ_GEOM,gid,velocity,0)
                point_velocity=velocity[3:]+np.cross(velocity[:3],con.pos-d.geom_xpos[gid])
                slips.append(float(np.linalg.norm(point_velocity[:2])))
        if i%4==0:
            for idx,name in enumerate(['foot_-1','foot_1']):
                gid=m.geom(name).id;mesh=m.geom_dataid[gid];startv=m.mesh_vertadr[mesh];count=m.mesh_vertnum[mesh]
                vertices=m.mesh_vert[startv:startv+count]@d.geom_xmat[gid].reshape(3,3).T+d.geom_xpos[gid]
                max_clearance[idx]=max(max_clearance[idx],float(vertices[:,2].min()))
        state=1 if contact==[True,False] else 2 if contact==[False,True] else 0
        if state:
            single[state-1]+=.005
            if state==pending:dwell+=.005
            else:pending=state;dwell=.005
            if dwell>=.025:
                if last and state!=last:alternations+=1
                last=state
        else:pending=0;dwell=0
        if trace and i%4==0:motion.append([float(d.time),*map(float,d.qpos),float(d.actuator_force[0])])
        if tilt>55 or d.subtree_com[m.body('assembly_A').id,2]<.015:
            fallen=True;break
    end=d.subtree_com[m.body('assembly_A').id].copy();dist=end-com0
    duration=float(d.time)
    # Conservative screen: upright >= requested duration, alternating support,
    # forward travel > one foot length; turning/drift are reported separately.
    success=not fallen and duration>=seconds-.01 and alternations>=6 and dist[0]>.06 and abs(dist[1])<.06
    result=dict(motor_model='continuous_affine_back_emf_v2',config=c,seconds=round(duration,3),total_mass_g=round(sum(m.body_mass)*1000,2),
        initial_com_mm=np.round(com0*1000,2).tolist(),travel_mm=np.round(dist*1000,2).tolist(),
        max_tilt_deg=round(max_tilt,2),alternating_support_transitions=alternations,
        single_support_seconds=single,peak_torque_Nm=round(max(forces),5),
        hard_stop_fraction=round(stop_time/duration,3),near_zero_speed_under_power_fraction=round(stalled/duration,3),
        upright=not fallen,walking_screen_pass=bool(success),hardware_validated=False)
    result['score']=(100 if not fallen else 0)+min(dist[0]*1000,120)+min(alternations,20)*2-max_tilt*.4-abs(dist[1])*500
    R=d.xmat[m.body('assembly_A').id].reshape(3,3)
    result['final_yaw_deg']=round(math.degrees(math.atan2(R[1,0],R[0,0])),2)
    result['max_entire_foot_clearance_mm']=[round(x*1000,2) for x in max_clearance]
    result['mean_contact_tangent_speed_mm_s']=round(float(np.mean(slips))*1000,2) if slips else None
    return result,m,d,motion

def sweep():
    rng=np.random.default_rng(20261026);results=[]
    for i in range(160):
        c=DEFAULT.copy()
        c.update(frequency=float(rng.choice([1.0,1.5,2.,2.5,3.])),duty=float(rng.choice([.15,.25,.4,.6])),
            gap=float(rng.choice([.022,.028,.034,.040])),rear=float(rng.choice([.006,.010,.014])),
            limit_deg=float(rng.choice([10,16,22])),battery_z=float(rng.choice([.032,.040,.048])),battery_y=.034)
        r,_,_,_=run(c);results.append(r)
        if i%20==0:print(f'tested {i+1}/160; best score {max(x["score"] for x in results):.1f}',flush=True)
    results.sort(key=lambda x:x['score'],reverse=True)
    (OUT/'outboard_sweep.json').write_text(json.dumps(results,indent=2))
    (OUT/'best_config.json').write_text(json.dumps(results[0]['config'],indent=2))
    print(json.dumps(results[:3],indent=2))

def live(c):
    import mujoco.viewer
    m,d=build(c,OUT/'corrected_hip.xml');flags={'pause':False,'reset':False}
    def key(k):
        if k==ord('P'):flags['pause']=not flags['pause']
        if k==ord('R'):flags['reset']=True
    with mujoco.viewer.launch_passive(m,d,key_callback=key) as v:
        v.cam.lookat[:]=[0,0,.055];v.cam.distance=.30;v.cam.azimuth=125;v.cam.elevation=-18
        while v.is_running():
            now=time.perf_counter()
            if flags['reset']:mujoco.mj_resetData(m,d);mujoco.mj_forward(m,d);flags['reset']=False
            if not flags['pause']:
                command(m,d,c);mujoco.mj_step(m,d,nstep=5)
            v.sync();time.sleep(max(0,.005-(time.perf_counter()-now)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sweep',action='store_true');p.add_argument('--view',action='store_true');a=p.parse_args()
    if a.sweep:sweep()
    else:
        config_path=next((OUT/name for name in ['audio_demo_config.json','recommended_research_config.json','best_config.json'] if (OUT/name).exists()),None)
        c=json.loads(config_path.read_text()) if config_path else DEFAULT.copy()
        if a.view:live(c)
        else:
            result,m,d,trace=run(c,12,True)
            result['clearance']=clearance_audit(c)
            (OUT/'best_trial.json').write_text(json.dumps(result,indent=2));print(json.dumps(result,indent=2))
            build(c,OUT/'corrected_hip.xml')
