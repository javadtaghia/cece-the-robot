"""One DC motor, opposite foot cranks and mechanically phased battery slider.
Foot orientation guides are ideal 1:1 constraints, not validated bearing/link CAD.
Slider-crank is an explicit closed loop. Free-base dynamics, no body animation.
"""
import argparse,json,math,time
import xml.etree.ElementTree as E
import numpy as np
import mujoco
from chick_sim import add,vec
from drive_study import OUT

DEFAULT=dict(crank=.006,shift=.025,rod=.050,half_span=.018,foot_half_width=.015,
    foot_half_length=.023,frequency=.65,stall=.0363,no_load=6.807,friction=.65,
    shift_enabled=True,payload_scale=1.,duty_limit=.85)

def build(c,save=None):
    root=E.Element('mujoco',model='CeCe crank and battery-shift drive - transmission study')
    add(root,'compiler',angle='radian');add(root,'option',timestep='.001',integrator='implicitfast',iterations='100')
    visual=add(root,'visual');add(visual,'global',offwidth='1000',offheight='800')
    default=add(root,'default');add(default,'joint',damping='.00005',armature='.000001')
    add(default,'geom',friction=f'{c["friction"]} .001 .00002',condim='4',solref='.006 1')
    world=add(root,'worldbody');add(world,'light',pos='0 -1 2')
    add(world,'geom',name='floor',type='plane',size='3 3 .01',rgba='.7 .77 .8 1')
    frame=add(world,'body',name='frame',pos=f'0 0 {.035+c["crank"]+.0004}')
    add(frame,'freejoint',name='free_base')
    add(frame,'geom',name='chassis',type='box',size='.032 .025 .003',pos='0 0 .008',mass='.012',rgba='.35 .4 .45 1')
    add(frame,'geom',name='N20',type='box',size='.006 .013 .005',pos='0 0 0',mass='.010',rgba='.6 .65 .7 1',contype='0',conaffinity='0')
    add(frame,'geom',name='fixed_electronics',type='box',size='.02 .018 .004',pos='0 0 .050',mass='.014',rgba='.1 .6 .3 1',contype='0',conaffinity='0')
    add(frame,'geom',name='head_audio_payload',type='ellipsoid',size='.024 .022 .020',pos='.007 0 .078',mass=.005*c['payload_scale'],rgba='1 .8 .2 .4',group='1')
    add(frame,'geom',name='lower_audio',type='box',size='.015 .008 .010',pos='.012 0 .023',mass=.013*c['payload_scale'],rgba='.2 .4 .5 1',contype='0',conaffinity='0')
    shaft=add(frame,'body',name='shaft')
    add(shaft,'joint',name='shaft',axis='0 1 0')
    add(shaft,'geom',name='shaft_metal',type='capsule',fromto='0 -.025 0 0 .025 0',size='.002',mass='.003',rgba='.5 .55 .6 1',contype='0',conaffinity='0')
    eq=add(root,'equality')
    for sign in [-1,1]:
        y=sign*c['half_span'];r=-sign*c['crank']
        add(shaft,'geom',name=f'crank_{sign}',type='capsule',fromto=vec([0,y,0,0,y,r]),size='.002',mass='.0015',rgba='.85 .2 .15 1',contype='0',conaffinity='0')
        carrier=add(shaft,'body',name=f'foot_carrier_{sign}',pos=vec([0,y,r]))
        add(carrier,'joint',name=f'guide_{sign}',axis='0 1 0')
        add(carrier,'geom',name=f'leg_{sign}',type='capsule',fromto='0 0 0 0 0 -.032',size='.0025',mass='.003',rgba='.75 .6 .2 1',contype='0',conaffinity='0')
        add(carrier,'geom',name=f'foot_{sign}',type='box',pos='0 0 -.032',size=vec([c['foot_half_length'],c['foot_half_width'],.003]),mass='.007',rgba='1 .45 .05 1')
        add(eq,'joint',name=f'orientation_guide_{sign}',joint1=f'guide_{sign}',joint2='shaft',polycoef='0 -1 0 0 0',solref='.003 1')
    r=c['shift'] if c['shift_enabled'] else .0001;L=c['rod'];z=.019
    roll=add(frame,'body',name='shift_crank',pos=vec([-.029,-L,z]))
    add(roll,'joint',name='bevel_output',axis='1 0 0')
    add(roll,'geom',name='shift_crank_bar',type='capsule',fromto=vec([0,0,0,0,r,0]),size='.002',mass='.002',rgba='.8 .25 .2 1',contype='0',conaffinity='0')
    rod=add(roll,'body',name='connecting_rod',pos=vec([0,r,0]))
    add(rod,'joint',name='rod_pivot',axis='1 0 0')
    add(rod,'geom',name='rod_bar',type='capsule',fromto=vec([0,0,0,0,L,0]),size='.0015',mass='.002',rgba='.4 .45 .5 1',contype='0',conaffinity='0')
    add(rod,'site',name='rod_tip',pos=vec([0,L,0]),size='.001')
    slider=add(frame,'body',name='battery_carriage',pos=vec([0,r,z]))
    add(slider,'joint',name='carriage_slide',type='slide',axis='0 1 0',damping='.04')
    add(slider,'site',name='slider_pin',pos='-.029 0 0',size='.001')
    add(slider,'geom',name='battery_holder',type='box',size='.029 .018 .002',pos='0 0 -.009',mass='.005',rgba='.2 .23 .27 1',contype='0',conaffinity='0')
    for sign in [-1,1]:
        add(slider,'geom',name=f'AA_{sign}',type='cylinder',size='.00725 .02525',euler='0 1.570796 0',pos=f'0 {sign*.008} 0',mass='.024',rgba='.7 .73 .76 1',contype='0',conaffinity='0')
    add(eq,'joint',name='bevel_1to1',joint1='bevel_output',joint2='shaft',polycoef=vec([c.get('phase',0),1,0,0,0]),solref='.003 1')
    add(eq,'connect',name='slider_crank_closure',site1='rod_tip',site2='slider_pin',solref='.003 1')
    act=add(root,'actuator');add(act,'general',name='one_DC_motor',joint='shaft',gear='1',
        gainprm=vec([c['stall']]),biasprm=vec([0,0,-c['stall']/c['no_load']]),biastype='affine',
        ctrlrange='-1 1',ctrllimited='true',forcerange=f'-{c["stall"]} {c["stall"]}',forcelimited='true')
    xml=E.tostring(root,encoding='unicode')
    if save:save.write_text(xml)
    m=mujoco.MjModel.from_xml_string(xml);d=mujoco.MjData(m)
    phase=c.get('phase',0)
    d.qpos[m.joint('bevel_output').qposadr[0]]=phase
    d.qpos[m.joint('rod_pivot').qposadr[0]]=-phase-math.asin(r/L*math.sin(phase))
    d.qpos[m.joint('carriage_slide').qposadr[0]]=r*math.cos(phase)+math.sqrt(L*L-r*r*math.sin(phase)**2)-L-r
    mujoco.mj_forward(m,d)
    return m,d

def command(m,d,c):
    speed=d.qvel[m.joint('shaft').dofadr[0]]
    desired=2*math.pi*c['frequency']*min(1,max(0,(d.time-.3)/1.))
    # Speed loop requires an encoder; no joint trajectory or body pose imposed.
    request=.002*(desired-speed)
    duty=np.clip(request/c['stall']+speed/c['no_load'],-c['duty_limit'],c['duty_limit'])
    d.ctrl[0]=duty
    return float(duty)

def run(c,seconds=10,trace=False):
    m,d=build(c);start=d.subtree_com[m.body('frame').id].copy();max_tilt=0;peak=0;stalled=0;bad=set();speeds=[];rms=[];closure=0;history=[]
    settled=None;last=0;pending=0;dwell=0;switches=0;single=[0.,0.]
    for i in range(int(seconds/.005)):
        duty=command(m,d,c);mujoco.mj_step(m,d,nstep=5)
        R=d.xmat[m.body('frame').id].reshape(3,3);tilt=math.degrees(math.acos(np.clip(R[2,2],-1,1)));max_tilt=max(max_tilt,tilt)
        speed=float(d.qvel[m.joint('shaft').dofadr[0]]);speeds.append(speed);tau=float(d.actuator_force[0]);peak=max(peak,abs(tau));rms.append(tau*tau)
        if abs(duty)>.15 and abs(speed)<.1:stalled+=.005
        closure=max(closure,float(np.linalg.norm(d.site_xpos[m.site('rod_tip').id]-d.site_xpos[m.site('slider_pin').id])))
        contacts=[False,False]
        for con in d.contact:
            a=m.geom(con.geom1).name;b=m.geom(con.geom2).name
            if 'floor' in [a,b]:
                other=b if a=='floor' else a
                if other=='foot_-1':contacts[0]=True
                elif other=='foot_1':contacts[1]=True
                else:bad.add(other)
        state=1 if contacts==[True,False] else 2 if contacts==[False,True] else 0
        if state:
            single[state-1]+=.005
            if state==pending:dwell+=.005
            else:pending=state;dwell=.005
            if dwell>=.025:
                if last and state!=last:switches+=1
                last=state
        else:pending=0;dwell=0
        if settled is None and d.time>=2:settled=d.subtree_com[m.body('frame').id].copy()
        if trace and i%4==0:history.append([float(d.time),*map(float,d.qpos)])
        if tilt>50 or bad:break
    end=d.subtree_com[m.body('frame').id].copy();travel=end-start
    return dict(motor_model='continuous_affine_back_emf_v2',config=c,seconds=round(float(d.time),3),mass_g=round(sum(m.body_mass)*1000,2),
        shaft_revolutions=round(float(d.qpos[m.joint('shaft').qposadr[0]])/(2*math.pi),3),
        average_shaft_speed_rad_s=round(float(np.mean(speeds)),3),
        travel_mm=np.round(travel*1000,2).tolist(),max_tilt_deg=round(max_tilt,2),
        after_settle_travel_mm=np.round((end-settled)*1000,2).tolist() if settled is not None else None,
        support_switches=switches,single_support_seconds=single,peak_torque_Nm=round(peak,5),
        rms_torque_Nm=round(math.sqrt(np.mean(rms)),5),stall_fraction=round(stalled/max(d.time,.001),3),
        closure_error_mm=round(closure*1000,3),nonfoot_floor_contacts=list(bad),
        upright=bool(max_tilt<50 and not bad and d.time>=seconds-.01),
        hardware_validated=False),m,d,history

def sweep():
    results=[]
    for f in [.35,.5,.65,.8]:
        for shift in [.015,.025,.035]:
            for width in [.012,.018,.023]:
                c=DEFAULT.copy();c.update(frequency=f,shift=shift,foot_half_width=width,half_span=width+.003)
                r,_,_,_=run(c,8);results.append(r)
        print(f'completed frequency {f}',flush=True)
    for r in results:
        r['score']=(100 if r['upright'] else 0)+r['travel_mm'][0]-abs(r['travel_mm'][1])*.5-r['max_tilt_deg']
    results.sort(key=lambda r:r['score'],reverse=True)
    (OUT/'crank_sweep.json').write_text(json.dumps(results,indent=2))
    (OUT/'crank_config.json').write_text(json.dumps(results[0]['config'],indent=2))
    print(json.dumps(results[:3],indent=2))

def live(c):
    import mujoco.viewer
    m,d=build(c,OUT/'crank_drive.xml');flags={'pause':False,'reset':False}
    def key(k):
        if k==ord('P'):flags['pause']=not flags['pause']
        if k==ord('R'):flags['reset']=True
    with mujoco.viewer.launch_passive(m,d,key_callback=key) as v:
        v.cam.lookat[:]=[0,0,.065];v.cam.distance=.35;v.cam.azimuth=120;v.cam.elevation=-20
        while v.is_running():
            tick=time.perf_counter()
            if flags['reset']:mujoco.mj_resetData(m,d);mujoco.mj_forward(m,d);flags['reset']=False
            if not flags['pause']:command(m,d,c);mujoco.mj_step(m,d,nstep=5)
            v.sync();time.sleep(max(0,.005-(time.perf_counter()-tick)))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--sweep',action='store_true');p.add_argument('--view',action='store_true');args=p.parse_args()
    if args.sweep:sweep()
    else:
        c=json.loads((OUT/'crank_config.json').read_text()) if (OUT/'crank_config.json').exists() else DEFAULT.copy()
        if args.view:live(c)
        else:
            r,m,d,h=run(c,15,True);(OUT/'crank_trial.json').write_text(json.dumps(r,indent=2));print(json.dumps(r,indent=2));build(c,OUT/'crank_drive.xml')
