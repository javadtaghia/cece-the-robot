"""Run the Cece 2 candidate on the existing Gazebo robot's four joint topics.

Stop the old gait controller before using this. Does not flash or command an ESP.
"""
import argparse,math,time
from pathlib import Path
from gait import PROFILE,at_time

def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--steps',type=int,default=10,help='Number of half-steps; must be positive')
    args=parser.parse_args()
    if args.steps<=0:raise ValueError('Use a finite positive step count')
    from gz.transport13 import Node
    from gz.msgs10.double_pb2 import Double
    node=Node()
    names=('left_hip','left_ankle','right_hip','right_ankle')
    pubs=[node.advertise('/cece/'+n,Double) for n in names]
    time.sleep(1.5)
    if not all(p.has_connections() for p in pubs):
        raise RuntimeError('Start the existing Cece Gazebo world first; joint controllers are missing')
    def send(angles):
        for pub,angle in zip(pubs,angles):
            msg=Double();msg.data=math.radians(angle);pub.publish(msg)
    # A robot toppled or displaced by an earlier run must be reset in Gazebo.
    send([0,0,0,0]);time.sleep(1)
    duration=args.steps*sum(PROFILE['phase_durations_s'])
    stop_file=Path(__file__).resolve().parent.parent/'cece'/'ros2_sim'/'generated'/'.cece_stop'
    start=time.monotonic();deadline=start
    try:
        while time.monotonic()-start<duration and not stop_file.exists():
            send(at_time(time.monotonic()-start))
            deadline+=1/PROFILE['command_hz']
            time.sleep(max(0,deadline-time.monotonic()))
    finally:
        # Ease toward neutral instead of a sudden full-angle target jump.
        end=at_time(max(0,time.monotonic()-start))
        for i in range(1,26):
            u=i/25;e=u*u*(3-2*u)
            send([a*(1-e) for a in end]);time.sleep(.02)
        send([0,0,0,0])
    print('Cece 2 targets sent. Observe Gazebo contacts and measured travel separately.')

if __name__=='__main__':main()
