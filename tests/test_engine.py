
import unittest
from ipc_calc.engine import IPC7351Engine

class TestIPCEngine(unittest.TestCase):
    def setUp(self):
        self.engine = IPC7351Engine()

    def test_bga_calculation_small_ball(self):
        # ball < 0.75 -> reduction 0.20
        # example: 0.5mm ball
        # Land = 0.5 * (1 - 0.20) = 0.4
        res = self.engine.calculate_bga(0.5)
        self.assertAlmostEqual(res['Land'], 0.40)
        self.assertAlmostEqual(res['CL'], 1.5)
        self.assertAlmostEqual(res['CW'], 1.5)

    def test_bga_calculation_large_ball(self):
        # ball >= 0.75 -> reduction 0.25
        # example: 0.8mm ball
        # Land = 0.8 * (1 - 0.25) = 0.6
        res = self.engine.calculate_bga(0.8)
        self.assertAlmostEqual(res['Land'], 0.60)
        self.assertAlmostEqual(res['CL'], 1.8)
        self.assertAlmostEqual(res['CW'], 1.8)

    def test_gull_wing_calculation(self):
        # Placeholder values to verify formula execution without crashing
        # L_min=1.0, L_max=1.2 (c_l=0.2)
        # W_min=1.0, W_max=1.2 (c_w=0.2)
        # T_min=0.4, T_max=0.5 (c_t=0.1)
        # Family Gull-wing, Level B
        res = self.engine.calculate_land_pattern(
            l_min=1.0, l_max=1.2,
            w_min=1.0, w_max=1.2,
            t_min=0.4, t_max=0.5,
            family="Gull-wing", level="B"
        )
        self.assertTrue("Z" in res)
        self.assertTrue("G" in res)
        self.assertTrue("X" in res)
        self.assertTrue("CL" in res)
        self.assertTrue("CW" in res)
        # Sanity check: Z (Outer) > G (Inner)
        self.assertGreater(res["Z"], res["G"])

if __name__ == '__main__':
    unittest.main()
