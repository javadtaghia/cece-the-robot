"""Export startup and steady gait separately to avoid a hip jump at loop wrap."""
from pathlib import Path
import hashlib,json,math,re,sys
HERE=Path(__file__).resolve().parent;REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'experiments/cece2'))
from gait import PROFILE,at_time
half=sum(PROFILE['phase_durations_s']);hz=PROFILE['command_hz']
n=round(half*hz);order=[0,2,1,3] # hardware 1=LH,2=RH,3=LA,4=RA
startup=[[round(at_time(i/hz)[j]*100) for j in order] for i in range(n)]
cycle=[[round(at_time(half+i/hz)[j]*100) for j in order] for i in range(2*n)]
def array(name,rows):
    return 'const int16_t '+name+'[][4] = {\n'+''.join('  {'+', '.join(map(str,row))+'},\n' for row in rows)+'};\n'
block=f'const uint16_t STARTUP_FRAMES = {n};\nconst uint16_t CYCLE_FRAMES = {2*n};\n'
block+=array('STARTUP_CDEG',startup)+array('CYCLE_CDEG',cycle)
p=HERE/'DueCeceFourServoWalk/DueCeceFourServoWalk.ino'
sketch=p.read_text(encoding='utf-8-sig');a,rest=sketch.split('// BEGIN GENERATED FOUR SERVO GAIT',1)
_,b=rest.split('// END GENERATED FOUR SERVO GAIT',1)
sketch=a+'// BEGIN GENERATED FOUR SERVO GAIT\n'+block+'// END GENERATED FOUR SERVO GAIT'+b
p.write_text(sketch,encoding='utf-8')
# Read the tables back from the actual delivered single-file sketch.
def parse(name):
    body=sketch.split(name+'[][4] = {',1)[1].split('};',1)[0]
    return [[int(v) for v in re.findall(r'-?\d+',row)] for row in re.findall(r'\{([^{}]+)\}',body)]
first=parse('STARTUP_CDEG');loop=parse('CYCLE_CDEG')
def row(frame):return first[frame] if frame<n else loop[(frame-n)%(2*n)]
node_error=0.;interpolation_error=0.;pulses=[[] for _ in range(4)]
for tick in range((n+2*n*10)*2):
    real_ms=tick*20;frame=real_ms//40;f=(real_ms%40)/40
    angles=[((1-f)*x+f*y)/100 for x,y in zip(row(frame),row(frame+1))]
    reference=[at_time(real_ms/2000)[j] for j in order]
    error=max(abs(a-b) for a,b in zip(angles,reference))
    interpolation_error=max(interpolation_error,error)
    if f==0:node_error=max(node_error,error)
    for k,(angle,sign) in enumerate(zip(angles,(1,-1,1,-1))):
        raw=sign*angle*10
        pulse=1500+(math.floor(raw+.5) if raw>=0 else -math.floor(-raw+.5))
        assert 1100<=pulse<=1900
        pulses[k].append(pulse)
assert node_error<=.0050001
assert interpolation_error<1.3
# The periodic hip reference must not jump from -15 degrees back to zero.
assert row(n+2*n)==cycle[0]
assert max(abs(a-b) for a,b in zip(row(n+2*n-1),row(n+2*n)))<400
report={'hardware_mapping_confirmed_by_user':True,
 'motors':[{'number':i+1,'pin':pin,'joint':joint,'direction':sign,'pulse_range_us':[min(pulses[i]),max(pulses[i])]} for i,(pin,joint,sign) in enumerate(zip((6,7,8,9),('left_hip','right_hip','left_ankle','right_ankle'),(1,-1,1,-1)))],
 'reference_hz':50,'output_hz':50,'time_scale':2,'first_half_step_s':half*2,
 'steady_cycle_s':half*4,'full_reference_amplitude':True,
 'max_node_error_deg':node_error,'max_interpolation_error_deg':interpolation_error,
 'cycles_checked':10,'physical_joint_calibration_verified':False,'physical_walking_verified':False,
 'source_sha256':hashlib.sha256((REPO/'experiments/cece2/gait.py').read_bytes()).hexdigest()}
(HERE/'four_servo_walk_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
