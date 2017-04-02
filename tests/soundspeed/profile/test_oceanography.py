import unittest
import numpy as np

from hydroffice.soundspeed.profile.oceanography import Oceanography as Oc


class TestSoundSpeedOceanography(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_p2d_gsw(self):
        # check values from generate_gsw_trusted_values
        trusted_gsw_d = 9713.7  # m
        trusted_gsw_p = 10000  # dBar
        trusted_gsw_lat = 30.0

        calc_d = Oc.p2d_gsw(p=trusted_gsw_p, lat=trusted_gsw_lat, dyn_height=None)
        self.assertAlmostEqual(calc_d, trusted_gsw_d, places=1)

    def test_p2d_backup(self):
        # check values from Fofonoff and Millard(1983)
        trusted_fof_d = 9712.653  # m
        trusted_fof_p = 10000  # dBar
        trusted_fof_lat = 30.0

        calc_d = Oc.p2d_backup(p=trusted_fof_p, lat=trusted_fof_lat)
        self.assertAlmostEqual(calc_d, trusted_fof_d, places=1)

    def test_d2p_gsw(self):
        # check values from generate_gsw_trusted_values
        trusted_gsw_d = 9713.7  # m
        trusted_gsw_p = 10000  # dBar
        trusted_gsw_lat = 30.0

        calc_p = Oc.d2p_gsw(d=trusted_gsw_d, lat=trusted_gsw_lat, dyn_height=None)
        self.assertAlmostEqual(calc_p, trusted_gsw_p, places=1)

    def test_d2p_backup(self):
        # check values from Fofonoff and Millard(1983)
        trusted_fof_d = 9712.653  # m
        trusted_fof_p = 10000  # dBar
        trusted_fof_lat = 30.0

        calc_p = Oc.d2p_backup(d=trusted_fof_d, lat=trusted_fof_lat)
        self.assertAlmostEqual(calc_p, trusted_fof_p, places=1)

    def test_speed(self):
        # check values from Fofonoff and Millard(1983)
        trusted_fof_d = 9712.653  # m
        trusted_fof_lat = 30.0

        # check values dBar from Wong and Zhu(1995), Table III
        trusted_fof_s = 35  # ppt
        trusted_fof_t = 20  # deg C
        trusted_fof_vs = 1687.198  # m/sec

        calc_vs = Oc.speed(d=trusted_fof_d, t=trusted_fof_t, s=trusted_fof_s, lat=trusted_fof_lat)

        self.assertAlmostEqual(calc_vs, trusted_fof_vs, places=1)

    def test_sal(self):
        # check values from Fofonoff and Millard(1983)
        trusted_fof_d = 9712.653  # m
        trusted_fof_lat = 30.0

        # check values dBar from Wong and Zhu(1995), Table III
        trusted_fof_s = 35  # ppt
        trusted_fof_t = 20  # deg C
        trusted_fof_vs = 1687.198  # m/sec

        calc_s = Oc.sal(d=trusted_fof_d, speed=trusted_fof_vs, t=trusted_fof_t, lat=trusted_fof_lat)

        self.assertAlmostEqual(calc_s, trusted_fof_s, places=1)

    def test_atg(self):
        # check values from Fofonoff and Millard(1983)
        atg_ck = 3.255976e-4
        s_ck = 40.0
        t_ck = 40
        p_ck = 10000

        atg_calc = Oc.atg(s=s_ck, t=t_ck, p=p_ck)

        self.assertAlmostEqual(atg_calc, atg_ck, places=1)

    def test_theta_t0(self):
        theta_ck = 36.89073
        s_ck = 40
        t0_ck = 40
        p0_ck = 10000
        p_ref_ck = 0

        theta_calc = Oc.pot_temp(s=s_ck, t=t0_ck, p=p0_ck, pr=p_ref_ck)

        self.assertAlmostEqual(theta_calc, theta_ck, places=1)

        t0_calc = Oc.in_situ_temp(s=s_ck, t=theta_ck, p=p0_ck, pr=p_ref_ck)

        self.assertAlmostEqual(t0_calc, t0_ck, places=1)

    def test_cr2s(self):
        cr_ck = 1.1
        t_ck = 40.0
        s_ck = 38.999

        s_calc = Oc.cr2s(cr=cr_ck, t=t_ck)

        self.assertAlmostEqual(s_calc, s_ck, places=1)

    def test_c_s(self):
        c_ck = 75
        t_ck = 40
        p_ck = 10000
        s_ck = 36.616

        s_calc = Oc.c2s(c=c_ck, t=t_ck, p=p_ck)

        self.assertAlmostEqual(s_calc, s_ck, places=1)

        c_calc = Oc.s2c(s=s_calc, p=p_ck, t=t_ck)

        self.assertAlmostEqual(c_calc, c_ck, places=1)

    def test_dyn_height_1000(self):
        # absolute salinity
        sa = np.array([34.7118, 34.8915, 35.0256, 34.8472, 34.7366, 34.7324])
        # conservative temperature
        ct = np.array([28.8099, 28.4392, 22.7862, 10.2262, 6.8272, 4.3236])
        # sea pressure
        p = np.array([10.0, 50.0, 125.0, 250.0, 600.0, 1000.0])
        p_ref = 1000.0
        # golden reference values
        gold_ref = np.array([17.0392, 14.6659, 10.9129, 7.5679, 3.3935, 0])

        calc_out = Oc.geo_strf_dyn_height(sa=sa, ct=ct, p=p, p_ref=p_ref)

        for i, val in enumerate(gold_ref):
            self.assertAlmostEqual(calc_out[i], val, places=0)


def suite():
    s = unittest.TestSuite()
    s.addTests(unittest.TestLoader().loadTestsFromTestCase(TestSoundSpeedOceanography))
    return s
