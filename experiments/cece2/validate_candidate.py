"""Sensitivity checks for the selected Cece 2 gait, at 50 Hz target updates."""
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor
import json,subprocess,sys
HERE=Path(__file__).resolve().parent
cases=[('candidate_50hz',[]),('candidate_dt480',['--hz','480']),
    ('candidate_low_friction',['--friction','.4']),
    ('candidate_60g_payload',['--extra-payload-g','60']),
    ('candidate_torque_060',['--torque','.06']),
    ('candidate_torque_040',['--torque','.04']),
    ('candidate_speed_350',['--no-load-speed','350'])]
def run(case):
    name,extra=case
    cmd=[sys.executable,str(HERE/'simulate.py'),'--name',name,'--steps','40',
        '--hip-deg','20','--phase-seconds','1','--phase-weights','.12,.08,.24,.08,.12',
        '--command-hz','50',*extra]
    proc=subprocess.run(cmd,capture_output=True,text=True)
    if proc.returncode:raise RuntimeError(proc.stderr[-2000:])
    data=json.loads((HERE/'results'/f'bullet_{name}_results.json').read_text())
    r=data['result']
    row={'name':name,'speed_mm_s':round(-r['net_base_displacement_mm'][1]/r['simulated_gait_time_s'],3),
        'lift_land_count':r['observed_lift_and_land_count'],'requested_steps':40,'fell':r['fell'],
        'max_tilt_deg':r['max_body_tilt_deg'],
        'peak_motor_torque_Nm':r['peak_motor_torque_Nm'],
        'max_tracking_error_deg':r['max_joint_tracking_error_deg'],
        'stance_drift_mm':max((s['stance_foot_max_horizontal_drift_mm'] for s in r['step_evidence']),default=999),
        'stance_airborne_s':max((s['stance_foot_airborne_duration_s'] for s in r['step_evidence']),default=999)}
    row['screen_pass']=not row['fell'] and row['lift_land_count']==40 and row['stance_drift_mm']<=2 and row['stance_airborne_s']==0
    row['ten_x_speed']=row['speed_mm_s']>=21.22
    print(json.dumps(row),flush=True)
    return row
with ThreadPoolExecutor(max_workers=3) as pool:rows=list(pool.map(run,cases))
(HERE/'candidate_validation.json').write_text(json.dumps(rows,indent=2))
