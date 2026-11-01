"""Export degree offsets for inspection; these are not absolute servo angles."""
from pathlib import Path
import csv,json
from gait import PROFILE,at_time
HERE=Path(__file__).resolve().parent
def main():
    duration=10*sum(PROFILE['phase_durations_s'])
    with (HERE/'cece2_forward_50hz_offsets.csv').open('w',newline='') as f:
        writer=csv.writer(f)
        writer.writerow(['time_s','left_hip_offset_deg','left_ankle_offset_deg',
                         'right_hip_offset_deg','right_ankle_offset_deg'])
        for tick in range(round(duration*PROFILE['command_hz'])):
            t=tick/PROFILE['command_hz']
            writer.writerow([round(t,4),*[round(a,4) for a in at_time(t)]])
    (HERE/'profile.json').write_text(json.dumps(PROFILE,indent=2))
if __name__=='__main__':main()
