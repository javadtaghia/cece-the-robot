"""Reproduce the selected profile, its geometry trace, and sensitivity cases."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sys,hashlib
from gait import PROFILE
HERE=Path(__file__).resolve().parent
cases=[('selected_240',[]),('selected_480',['--hz','480']),
       ('selected_low_friction',['--friction','.4']),
       ('selected_60g_payload',['--extra-payload-g','60']),
       ('selected_torque_060',['--torque','.06']),
       ('selected_torque_040',['--torque','.04']),
       ('selected_speed_350',['--no-load-speed','350'])]
def run(case):
    name,extra=case
    proc=subprocess.run([sys.executable,str(HERE/'simulate.py'),'--name',name,
        '--steps','40','--hip-deg',str(PROFILE['hip_deg']),'--roll-deg',str(PROFILE['roll_deg']),
        '--phase-seconds','1','--phase-weights',','.join(map(str,PROFILE['phase_durations_s'])),
        '--command-hz',str(PROFILE['command_hz']),'--normalized-controller',*extra],capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr[-2000:])
    data=json.loads((HERE/'results'/f'bullet_{name}_results.json').read_text());r=data['result']
    row={'name':name,'speed_mm_s':round(-r['net_base_displacement_mm'][1]/r['simulated_gait_time_s'],3),
         'lifts':r['observed_lift_and_land_count'],'fell':r['fell'],
         'max_tilt_deg':r['max_body_tilt_deg'],'max_tracking_error_deg':r['max_joint_tracking_error_deg'],
         'stance_drift_mm':max((s['stance_foot_max_horizontal_drift_mm'] for s in r['step_evidence']),default=999),
         'contact_slip_integral_mm':max((s['stance_contact_slip_integral_mm'] for s in r['step_evidence']),default=999),
         'stance_airborne_s':max((s['stance_foot_airborne_duration_s'] for s in r['step_evidence']),default=999)}
    row['screen_pass']=not row['fell'] and row['lifts']==40 and row['stance_drift_mm']<=2 and row['stance_airborne_s']==0
    print(json.dumps(row),flush=True);return row
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,cases))
summary={'profile':PROFILE,'cases':rows,
    'source_sha256':{p:hashlib.sha256((HERE/p).read_bytes()).hexdigest() for p in ('simulate.py','gait.py')},
    'hardware_approved':False,'gazebo_measured':False,
    'acceptance':'40/40 lift-and-land, no fall, stance origin drift <=2 mm, no stance flight. Integrated contact slip is also reported, not assumed zero.'}
(HERE/'selected_validation.json').write_text(json.dumps(summary,indent=2))
