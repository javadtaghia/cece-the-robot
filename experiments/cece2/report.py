"""Summarize matched nominal comparisons without relabeling failed trials."""
from pathlib import Path
import json,hashlib
from result_io import load_result
HERE=Path(__file__).resolve().parent
def load(name):return load_result(name)
def speed(d):
    r=d['result'];return -r['net_base_displacement_mm'][1]/r['simulated_gait_time_s']
rows=[]
for hz in (240,480):
    baseline=load(f'finalist_3_{hz}');candidate=load(f'selected_{hz}')
    rows.append({'physics_hz':hz,'baseline_mm_s':speed(baseline),
                 'cece2_mm_s':speed(candidate),'speed_ratio':speed(candidate)/speed(baseline),
                 'candidate_lifts':candidate['result']['observed_lift_and_land_count'],
                 'candidate_fell':candidate['result']['fell']})
out={'nominal_comparisons':rows,'physical_walk_verified':False,
     'leg_geometry_changed':False,'main_cece_preserved':True,
     'selected_validation':'selected_validation.json',
     'source_cece1_sha256':hashlib.sha256((HERE.parent/'cece/bullet_gait/simulate_bullet.py').read_bytes()).hexdigest(),
     'scope':'Matched Bullet model comparisons with assumed actuators and contacts; not measured hardware or Gazebo performance.'}
(HERE/'comparison.json').write_text(json.dumps(out,indent=2))
print(json.dumps(out,indent=2))
