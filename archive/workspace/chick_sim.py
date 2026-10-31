"""CeCe packaging and one-motor mechanism experiment. SI units in MuJoCo.
Not a validated gait or selected motor. Run --check, --bench, or --walk.
"""
from pathlib import Path
import argparse, itertools, json, math, time
import xml.etree.ElementTree as ET
import numpy as np
import mujoco

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'out'
# mm, kg. Purchased envelopes are provisional, including connectors.
PARTS = [
    ('AA_holder', (-16, 0, 65.5), (18, 34, 55), .005, (.2,.23,.26)),
    ('AA_left', (-16, -8, 65.5), (14.5,14.5,50.5), .024, (.65,.7,.75)),
    ('AA_right', (-16, 8, 65.5), (14.5,14.5,50.5), .024, (.65,.7,.75)),
    ('SuperMini', (17,-3,78), (23,18,8), .004, (.1,.6,.3)),
    ('motor_driver_reserve', (17,-13,53), (20,14,6), .002, (.1,.6,.3)),
    ('regulator_reserve', (17,9,53), (20,16,8), .003, (.2,.4,.8)),
    ('audio_amp_reserve', (17,4,65), (20,18,6), .002, (.1,.6,.3)),
    ('speaker', (6,4,118), (30,5,20), .006, (.15,.17,.2)),
    ('mic_board_reserve', (14,-6,122), (16.5,4,12.7), .001, (.1,.6,.3)),
    ('N20_motor_reserve', (0,0,28), (12,26,10), .010, (.6,.65,.7)),
]
TORQUE = .020  # N m, illustrative output limit, NOT a motor specification
SPEED = 10.0   # rad/s illustrative no-load output speed

def vec(v): return ' '.join(f'{x:.7g}' for x in v)
def mm(v): return np.array(v, dtype=float)*.001
def add(p,t,**attrs): return ET.SubElement(p,t,{k:str(v) for k,v in attrs.items()})

def make_sole():
    """Convex sphere-clipped rectangular sole matching the SCAD concept (metres)."""
    verts=[]; faces=[]; n=10
    for top in [False,True]:
        for i in range(n+1):
            for j in range(n+1):
                x=-18+36*i/n; y=-12+24*j/n
                z=8 if top else 45-math.sqrt(45**2-x*x-y*y)
                verts.append((x*.001,y*.001,z*.001))
    offset=(n+1)**2
    for i in range(n):
        for j in range(n):
            a=i*(n+1)+j; b=a+1; c=a+n+1; d=c+1
            faces += [(a,c,b),(b,c,d),(a+offset,b+offset,c+offset),(b+offset,d+offset,c+offset)]
    for edge in [[j for j in range(n+1)], [n*(n+1)+j for j in range(n+1)],
                 [i*(n+1) for i in range(n+1)], [i*(n+1)+n for i in range(n+1)]]:
        for a,b in zip(edge,edge[1:]): faces += [(a,b,a+offset),(b,b+offset,a+offset)]
    # Orient every convex surface triangle outward for correct rendering.
    centre=np.mean(verts,axis=0)
    oriented=[]
    for a,b,c in faces:
        pa,pb,pc=(np.array(verts[k]) for k in [a,b,c])
        if np.dot(np.cross(pb-pa,pc-pa),(pa+pb+pc)/3-centre)<0: b,c=c,b
        oriented.append((a,b,c))
    faces=oriented
    path=OUT/'sole.obj'
    path.write_text('\n'.join(['v '+vec(v) for v in verts]+['f '+vec([x+1 for x in f]) for f in faces]))
    return path

def build(bench=False, friction=.7):
    root=ET.Element('mujoco',model='CeCe BENCH fixture' if bench else 'CeCe FREE base experiment')
    add(root,'compiler',angle='radian')
    add(root,'option',timestep='.001',gravity='0 0 -9.81',integrator='implicitfast')
    vis=add(root,'visual'); add(vis,'global',offwidth='1000',offheight='800'); add(vis,'headlight',ambient='.6 .6 .6')
    default=add(root,'default'); add(default,'geom',friction=f'{friction} .005 .0001',solref='.01 1',condim='4')
    asset=add(root,'asset'); add(asset,'mesh',name='sole',file=str(make_sole()))
    world=add(root,'worldbody')
    add(world,'light',pos='0 -1 2',dir='0 0 -1')
    add(world,'geom',name='floor',type='plane',size='1 1 .01',rgba='.78 .82 .85 1')
    torso=add(world,'body',name='torso',pos='0 0 .0285')
    if not bench: add(torso,'freejoint',name='free_base')
    # Box represents shell outer envelope; mass is estimated hollow shell mass.
    add(torso,'geom',name='body_shell',type='box',pos='0 0 .039',size='.032 .024 .032',mass='.012',rgba='1 .78 .15 .28',group='1')
    add(torso,'geom',name='head_shell',type='ellipsoid',pos='.006 0 .091',size='.025 .022 .023',mass='.006',rgba='1 .83 .25 .35',group='1')
    add(torso,'geom',name='beak',type='ellipsoid',pos='.033 0 .083',size='.012 .007 .004',mass='.001',rgba='1 .4 .05 1')
    for sign in [-1,1]:
        add(torso,'geom',name=f'eye_{sign}',type='sphere',pos=f'.025 {sign*.013} .1',size='.003',mass='.0001',rgba='.1 .1 .1 1',contype='0',conaffinity='0')
    for name,centre,size,mass,col in PARTS:
        # Holder contains AA cells intentionally; shell contains the electronics.
        # Component packing is audited independently, not as self-colliding geoms.
        p=mm(centre)-np.array([0,0,.028])
        add(torso,'geom',name=name,type='box',pos=vec(p),size=vec(mm(size)/2),mass=mass,
            rgba=vec((*col,.23 if name=='AA_holder' else 1)),group='2',contype='0',conaffinity='0')
    for side,y in [('right',-.018),('left',.018)]:
        leg=add(torso,'body',name=side+'_leg',pos=f'0 {y} 0')
        if side=='left': add(leg,'joint',name='hip',axis='0 1 0',range='-.35 .35',damping='.00015',armature='.000003',frictionloss='.00015')
        add(leg,'geom',name=side+'_strut',type='capsule',fromto='0 0 0 0 0 -.020',size='.0025',mass='.002',rgba='.8 .5 .15 1')
        add(leg,'geom',name=side+'_foot',type='mesh',mesh='sole',pos='0 0 -.028',mass='.005',rgba='1 .45 .05 1')
        add(leg,'geom',name=side+'_hub',type='cylinder',euler='1.570796 0 0',size='.004 .002',mass='.001',rgba='.4 .45 .5 1')
    act=add(root,'actuator'); add(act,'motor',name='hip_output_torque',joint='hip',gear='1',ctrllimited='true',ctrlrange=f'-{TORQUE} {TORQUE}')
    path=OUT/('chick_bench.xml' if bench else 'chick_free.xml')
    ET.indent(root); ET.ElementTree(root).write(path,encoding='unicode')
    model=mujoco.MjModel.from_xml_path(str(path)); data=mujoco.MjData(model)
    mujoco.mj_forward(model,data)
    return model,data

def control(m,d):
    j=m.joint('hip'); q=d.qpos[j.qposadr[0]]; speed=d.qvel[j.dofadr[0]]
    ramp=min(d.time/1.0,1)
    target=math.radians(14)*math.sin(2*math.pi*1.5*d.time)*ramp
    request=.12*(target-q)-.0012*speed
    # Symmetric bounded torque-speed envelope, not an electrical motor model.
    cap=TORQUE*max(0,1-abs(speed)/SPEED)
    d.ctrl[0]=np.clip(request,-cap,cap)
    return target,q,float(d.ctrl[0])

def packaging():
    collisions=[]; outside=[]; separation=[]
    parts={p[0]:p for p in PARTS}
    for a,b in itertools.combinations(PARTS,2):
        if a[0]=='AA_holder' and b[0].startswith('AA_'): continue
        overlap=(np.array(a[2])+np.array(b[2]))/2-abs(np.array(a[1])-np.array(b[1]))
        if np.all(overlap>0): collisions.append({'a':a[0],'b':b[0],'overlap_mm':overlap.tolist()})
    for p in PARTS:
        if p[0] in ['speaker','mic_board_reserve','N20_motor_reserve']: continue
        low=np.array(p[1])-np.array(p[2])/2; high=np.array(p[1])+np.array(p[2])/2
        if np.any(low<[-30,-22,37]) or np.any(high>[30,22,97]): outside.append(p[0])
    # Check head components against its inner ellipsoid, at all box corners.
    for name in ['speaker','mic_board_reserve']:
        p=parts[name]
        worst=max(sum(((np.array(p[1])+np.array(s)*np.array(p[2])/2-[6,0,119])/[23,20,21])**2) for s in itertools.product([-1,1],repeat=3))
        if worst>1: outside.append(name)
    report={'component_overlap_pairs':collisions,'outside_cavity':outside,
            'static_envelope_fit_pass':not collisions and not outside,
            'proposed_height_mm':142,'body_outer_mm':[64,48,64],
            'two_AA_mass_g':48,'estimated_total_mass_g':round((sum(p[3] for p in PARTS)+.012+.006+.001+.0002+2*.008)*1000,1),
            'not_validated':['Measured purchased component dimensions and connectors','Mounts, bearings, shaft/coupler and wire routing','Microphone isolation and speaker enclosure response','Power conversion, AA voltage sag, motor current and selected motor torque','Shell split and fasteners','Detailed curved-surface and moving interference']}
    (OUT/'packaging_report.json').write_text(json.dumps(report,indent=2))
    return report

def scad():
    lines=['// Generated compact two-AA packaging study, mm. Not print-ready.', '$fn=48;',
           'module shell_box(){difference(){translate([0,0,67])cube([64,48,64],center=true);translate([0,0,67])cube([60,44,60],center=true);}}',
           'color([1,.78,.15,.2])shell_box();',
           'color([1,.83,.25,.2])translate([6,0,119])difference(){scale([25,22,23])sphere(1);scale([23,20,21])sphere(1);}',
           'color([1,.4,.05])translate([33,0,111])scale([12,7,4])sphere(1);']
    for name,c,s,mass,col in PARTS:
        lines.append(f'// {name}: estimated {mass*1000:g} g')
        lines.append(f'color([{",".join(map(str,(*col,.22 if name=="AA_holder" else 1)))}])translate([{",".join(map(str,c))}])cube([{",".join(map(str,s))}],center=true);')
    for y in [-18,18]:
        lines += [f'color("orange")translate([0,{y},0])intersection(){{translate([0,0,45])sphere(45);translate([0,0,4])cube([36,24,8],center=true);}}',
                  f'color("goldenrod")hull(){{translate([0,{y},8])sphere(2.5);translate([0,{y},28])sphere(2.5);}}']
    (ROOT/'chick_packaging.scad').write_text('\n'.join(lines))

def check():
    results=[]
    for bench,friction in [(True,.7),(False,.4),(False,.7),(False,1.)]:
        m,d=build(bench,friction); errors=[]; qs=[]; torques=[]; saturated=0; bad_contacts=set(); tilt=0
        start=d.xpos[m.body('torso').id].copy()
        for _ in range(6000):
            target,q,tau=control(m,d); mujoco.mj_step(m,d)
            if d.time>1: errors.append(target-q)
            qs.append(q); torques.append(tau); saturated+=abs(tau)>.95*TORQUE
            tilt=max(tilt,math.degrees(math.acos(np.clip(d.xmat[m.body('torso').id,8],-1,1))))
            for con in d.contact:
                a=m.geom(con.geom1).name; b=m.geom(con.geom2).name
                if 'floor' in [a,b] and not any(n.endswith('_foot') for n in [a,b]): bad_contacts.add(tuple(sorted([a,b])))
        end=d.xpos[m.body('torso').id].copy()
        results.append({'mode':'FIXED BENCH' if bench else 'FREE FLOOR','friction':friction,
          'hip_range_deg':[round(math.degrees(min(qs)),2),round(math.degrees(max(qs)),2)],
          'tracking_rms_deg':round(math.degrees(float(np.sqrt(np.mean(np.square(errors))))),2),
          'peak_output_torque_Nm':round(max(map(abs,torques)),5),'time_near_assumed_torque_limit_percent':round(saturated/60,1),
          'max_tilt_deg':round(tilt,1),'travel_mm':np.round((end-start)*1000,1).tolist(),
          'nonfoot_floor_contacts':sorted(bad_contacts),
          'remained_upright':tilt<45 and not bad_contacts,
          'motor_hardware_validated':False})
    report={'assumptions':{'output_torque_limit_Nm':TORQUE,'no_load_speed_rad_s':SPEED,'drive':'PD torque command approximates feedback control; encoder not yet specified','mechanism':'right leg rigid to torso, left leg hinged at hip; single motor hypothesis'},
            'packaging':packaging(),'trials':results,'walking_validated':False}
    (OUT/'simulation_report.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    # Still images from actual physics states; no animated body placement.
    m,d=build(True); renderer=mujoco.Renderer(m,height=800,width=1000)
    camera=mujoco.MjvCamera(); camera.lookat[:]=[0,0,.075]; camera.distance=.32; camera.azimuth=135; camera.elevation=-15
    for _ in range(1800): control(m,d); mujoco.mj_step(m,d)
    renderer.update_scene(d,camera=camera)
    from PIL import Image
    Image.fromarray(renderer.render()).save(OUT/'chick_sim_cutaway.png')
    renderer.close()

def live(bench):
    import mujoco.viewer
    m,d=build(bench); flags={'pause':False,'reset':False}
    def key(k):
        if k==ord('P'): flags['pause']=not flags['pause']
        if k==ord('R'): flags['reset']=True
    print('FIXED BENCH: actuator travel only' if bench else 'FREE FLOOR: unsupported physics experiment',flush=True)
    print('P pause/resume | R reset | use Rendering > geom groups to hide shell group 1 or internals group 2',flush=True)
    with mujoco.viewer.launch_passive(m,d,key_callback=key) as viewer:
        viewer.cam.lookat[:]=[0,0,.075]; viewer.cam.distance=.35; viewer.cam.azimuth=135; viewer.cam.elevation=-15
        while viewer.is_running():
            tick=time.perf_counter()
            if flags['reset']: mujoco.mj_resetData(m,d); mujoco.mj_forward(m,d); flags['reset']=False
            if not flags['pause']:
                for _ in range(10): control(m,d); mujoco.mj_step(m,d)
            viewer.sync(); time.sleep(max(0,.01-(time.perf_counter()-tick)))

if __name__=='__main__':
    parser=argparse.ArgumentParser(); mode=parser.add_mutually_exclusive_group()
    mode.add_argument('--check',action='store_true'); mode.add_argument('--bench',action='store_true'); mode.add_argument('--walk',action='store_true')
    args=parser.parse_args(); OUT.mkdir(exist_ok=True); scad()
    if args.check: check()
    else: live(not args.walk)
