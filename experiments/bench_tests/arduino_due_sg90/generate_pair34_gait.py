"""Export both Cece 2 ankle references for a reduced-range two-foot bench test."""
from pathlib import Path
import hashlib,json,math,sys
HERE=Path(__file__).resolve().parent; REPO=HERE.parents[2]
sys.path.insert(0,str(REPO/'experiments'/'cece2'))
from gait import PROFILE,at_time
count=round(2*sum(PROFILE['phase_durations_s'])*PROFILE['command_hz'])
left=[round(at_time(i/50)[1]*100) for i in range(count)]
right=[round(at_time(i/50)[3]*100) for i in range(count)]
def table(name,values):
    return 'const int16_t '+name+'[GAIT_SAMPLE_COUNT] = {\n'+''.join(
        '  '+', '.join(map(str,values[i:i+8]))+',\n' for i in range(0,count,8))+'};\n'
block='const uint16_t GAIT_SAMPLE_COUNT = '+str(count)+';\n'
block+=table('LEFT_ANKLE_CDEG',left)+table('RIGHT_ANKLE_CDEG',right)
ino=HERE/'DuePair34TestV5'/'DuePair34TestV5.ino'
text=ino.read_text(encoding='utf-8-sig')
start='// BEGIN GENERATED PAIR34 GAIT';end='// END GENERATED PAIR34 GAIT'
a,rest=text.split(start,1);_,b=rest.split(end,1)
ino.write_text(a+start+'\n'+block+end+b,encoding='utf-8')
# Check the actual runtime interpolation, gain and pulse limits over five cycles.
pulses=[[],[]];offsets=[[],[]];max_reference_error=0.
for frame in range(count*2*5):
    elapsed=frame*20
    i=(elapsed//40)%count;j=(i+1)%count;f=(elapsed%40)/40
    for k,values in enumerate((left,right)):
        off=((1-f)*values[i]+f*values[j])/100*.35
        off=max(-12,min(12,off))
        pulse=1500+math.floor(off*10+.5) if off>=0 else 1500-math.floor(-off*10+.5)
        pulse=max(1380,min(1620,pulse))
        offsets[k].append(off);pulses[k].append(pulse)
        reference=at_time(elapsed/2000)[(1,3)[k]]*.35
        max_reference_error=max(max_reference_error,abs(reference-off))
for row in pulses:
    assert min(row)<1500<max(row) and min(row)>=1380 and max(row)<=1620
    assert row[:count*2]==row[count*2:count*4]
report={'mode':'reduced paired-ankle bench test, not full walking',
 'pins':{'3':'Due D8, assumed left foot','4':'Due D9, assumed right foot'},
 'reference_joint_indices':[1,3],'reference_samples':count,
 'reference_gain':.35,'time_scale':2,'output_hz':50,
 'full_cycle_seconds':count*.04,'pulse_ranges_us':[[min(v),max(v)] for v in pulses],
 'nominal_offset_ranges_deg':[[min(v),max(v)] for v in offsets],
 'max_reference_interpolation_error_deg':max_reference_error,
 'cycles_checked':5,'physical_motion_verified':False,
 'source_sha256':hashlib.sha256((REPO/'experiments/cece2/gait.py').read_bytes()).hexdigest()}
(HERE/'pair34_gait_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
