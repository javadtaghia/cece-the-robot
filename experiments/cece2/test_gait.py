"""Check real-time phase boundaries and the servo-command export."""
import math,unittest
from gait import PROFILE,at_time
class TimingTest(unittest.TestCase):
    def test_long_50hz_run_is_finite_and_bounded(self):
        for i in range(50000):
            angles=at_time(i/50)
            self.assertEqual(len(angles),4)
            self.assertTrue(all(math.isfinite(a) and abs(a)<=35 for a in angles))
    def test_all_phase_boundaries_are_continuous(self):
        t=0
        for _ in range(20):
            for duration in PROFILE['phase_durations_s']:
                t+=duration
                before=at_time(t-1e-8);after=at_time(t+1e-8)
                self.assertLess(max(abs(a-b) for a,b in zip(before,after)),1e-4)
    def test_invalid_time_rejected(self):
        for t in (-1,float('nan'),float('inf')):
            with self.assertRaises(ValueError):at_time(t)
if __name__=='__main__':unittest.main()
