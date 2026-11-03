"""Export Cece 2 right-ankle targets at exactly 50 Hz for the Due bench test."""
from pathlib import Path
import hashlib,json,math,re,sys
HERE=Path(__file__).resolve().parent
REPO=HERE.parents[2]
CECE2=REPO/'experiments'/'cece2'
sys.path.insert(0,str(CECE2))
from gait import PROFILE,at_time
period=2*sum(PROFILE['phase_durations_s']);hz=PROFILE['command_hz']
count=round(period*hz)
assert math.isclose(count/hz,period)
values=[round(at_time(i/hz)[3]*100) for i in range(count)]
header='''// GENERATED from experiments/cece2/gait.py, joint index 3 (right ankle).
// Signed hundredths of a nominal degree relative to neutral.
#include <stdint.h>
const uint16_t GAIT_SAMPLE_MS = 20;
const uint16_t GAIT_SAMPLE_COUNT = %d;
const int16_t SERVO4_GAIT_CDEG[GAIT_SAMPLE_COUNT] = {
%s
};
'''%(count,'\n'.join('  '+', '.join(str(v) for v in values[i:i+8])+',' for i in range(0,count,8)))
path=HERE/'DueServo4SingleAnkleGait'/'DueServo4SingleAnkleGait.ino'
sketch=path.read_text(encoding='utf-8-sig')
start='// BEGIN GENERATED CECE2 SERVO4 GAIT'
end='// END GENERATED CECE2 SERVO4 GAIT'
before,rest=sketch.split(start,1)
_,after=rest.split(end,1)
path.write_text(before+start+'\n'+header+end+after,encoding='utf-8')
loaded=[int(v) for v in re.findall(r'-?\d+',header.split('= {')[1].split('};')[0])]
error=max(abs(loaded[i%count]/100-at_time(i/hz)[3]) for i in range(count*10))
assert error<=.0050001
report={'joint':'right_ankle','joint_index_zero_based':3,'bench_signal_pin':'Due D9',
 'sample_hz':hz,'cycle_seconds':period,'samples_per_cycle':count,
 'nominal_offset_deg':[min(values)/100,max(values)/100],
 'max_command_export_error_deg':error,'reference_comparison_cycles':10,
 'pulse_mapping':'1500 us + offset_degrees * 10 us/degree; uncalibrated hardware assumption',
 'physical_servo_tracking_verified':False,
 'source_gait_sha256':hashlib.sha256((CECE2/'gait.py').read_bytes()).hexdigest()}
(HERE/'servo4_gait_check.json').write_text(json.dumps(report,indent=2))
print(json.dumps(report,indent=2))
