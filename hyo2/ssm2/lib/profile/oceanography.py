import math
import numpy as np
import gsw
import logging
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
logger = logging.getLogger(__name__)


class Oceanography:
    """A collection of oceanographic methods

    main refs:
    - C-T. Chen and F.J. Millero, Speed of sound in seawater at high pressures (1977)
      J. Acoust. Soc. Am. 62(5) pp 1129-1135
    - N.P. Fofonoff and R.C. Millard Jr. Algorithms for computation of fundamental properties
      of seawater (1983), UNESCO technical papers in marine science. No. 44, Division
      of Marine Sciences. UNESCO, Place de Fontenoy, 75700 Paris.
    - J.M. Pike and F.L. Beiboer, A comparison between algorithms for the speed of sound
      in seawater (1993) The Hydrographic Society, Special Publication no. 34
    - G.S.K. Wong and S Zhu, Speed of sound in seawater as a function of salinity, temperature
      and pressure (1995) J. Acoust. Soc. Am. 97(3) pp 1732-1736
    - C. C. Leroy and F Parthiot, Depth-pressure relationship in the oceans and seas (1998)
      J. Acoust. Soc. Am. 103(3) pp 1346-1352
    """

    # ### PRESSURE/DEPTH METHODS ###

    @classmethod
    def p2d(cls, p, lat: float = 30.0, dyn_height: int | None = None, debug: bool = False) -> float:
        """Convert pressure to depth"""
        try:
            return cls.p2d_gsw(p=p, lat=lat, dyn_height=dyn_height)

        except Exception as e:
            if debug:
                logger.info("using backup: %s" % e)
            return cls.p2d_backup(p=p, lat=lat)

    @classmethod
    def p2d_gsw(cls, p, lat: float, dyn_height: int | None) -> float:

        if not isinstance(p, np.ndarray):
            p = np.array(p, ndmin=1, copy=False)

        if dyn_height is None:
            depth = -gsw.conversions.z_from_p(p=p, lat=lat)
            return depth[0]

        depth = -gsw.conversions.z_from_p(p=p, lat=lat, geo_strf_dyn_height=dyn_height)
        for val in depth:
            if np.isnan(val):
                logger.info("nan in gsw.conversions.z_from_p with dyn_height")
                return -gsw.conversions.z_from_p(p=p, lat=lat)

        return depth[0]

    @classmethod
    def p2d_backup(cls, p, lat: float) -> float:
        """Convert pressure to depth

        If the latitude is not passed, a default value of 30.0 is used.
        Declared precision: 0.0002 m or better in range 0-12,000 decibars.
        ref: Fofonoff and Millard(1983)

        Args:
            p: pressure in decibars
            lat: latitude in decimal degrees

        Returns: depth in metres

        """

        # (sin of latitude) squared
        sl = np.sin(lat / 57.29578)
        sl2 = sl * sl

        # gravity variation with pressure and latitude (ref: Anon.(1970), Bulletin Geodesique)
        g = 9.780318 * (1.0 + (5.2788e-3 + 2.36e-5 * sl2) * sl2) + 1.092e-6 * p

        d = (((-1.82e-15 * p + 2.279e-10) * p - 2.2512e-5) * p + 9.72659) * p

        return d / g

    @classmethod
    def d2p(cls, d, lat: float = 30.0, dyn_height: int | None = None, debug: bool = False) -> float:
        """Convert pressure to depth"""
        try:
            return cls.d2p_gsw(d=d, lat=lat, dyn_height=dyn_height)

        except RuntimeError:
            if debug:
                logger.info("using backup")
            return cls.d2p_backup(d=d, lat=lat)

    @classmethod
    def d2p_gsw(cls, d, lat: float, dyn_height: int | None) -> float:

        if not isinstance(d, np.ndarray):
            d = np.array(d, ndmin=1, copy=False)

        if dyn_height is None:
            pressure = gsw.conversions.p_from_z(z=-d, lat=lat)
            return pressure[0]

        pressure = gsw.conversions.p_from_z(z=-d, lat=lat, geo_strf_dyn_height=dyn_height)
        for val in pressure:
            if np.isnan(val):
                logger.info("nan in gsw.conversions.p_from_z with dyn_height")
                return gsw.conversions.p_from_z(z=-d, lat=lat)

        return pressure[0]

    @classmethod
    def d2p_backup(cls, d, lat: float) -> float:
        """Convert depth to pressure

        ref: Leroy and Parthiot(1998)

        Args:
            d: depth in metres
            lat: latitude in decimal degrees
        Returns: pressure in decibar

        """
        # (sin of latitude) squared
        sl = np.sin(lat / 57.29578)
        sl2 = sl * sl

        # gravity variation with latitude
        g = 9.7803 * (1 + 5.3e-3 * sl2)

        h45 = 1.00818e-2 * d + 2.465e-8 * d ** 2 - 1.25e-13 * d ** 3 + 2.8e-19 * d ** 4
        k = (g - 2e-5 * d) / (9.80612 - 2e-5 * d)
        hlat = h45 * k

        # TODO: Leroy and Parthiot(1998) also has table of corrections for specific seas
        # e.g.: correction applicable to common oceans
        # corr = 1e-2 * (d / (d + 100)) + 6.2e-6 * d

        return 100.0 * hlat  # from MPa to decibar

    # ### SPEED METHODS ###

    @classmethod
    def speed(cls, d, t, s, lat=30):
        """ Calculate sound speed from depth, temperature, and salinity

        validity: 0 - 40 deg C, 0 - 40 ppt, 0 - 1000 bars (~1000m)

        ref: Wong and Zhu(1995), Chen and Millero(1977)

        Args:
            d: depth in meter
            t: temp in degrees celsius
            s: salinity in practical salinity units (ppt)
            lat: latitude in decimal degree

        Returns: sound speed in m/s
        """

        p = cls.d2p_backup(d, lat) / 10  # pressure in bar

        c00 = 1402.388
        c01 = 5.03830
        c02 = -5.81090e-2
        c03 = 3.3432e-4
        c04 = -1.47797e-6
        c05 = 3.1419e-9
        c10 = 0.153563
        c11 = 6.8999e-4
        c12 = -8.1829e-6
        c13 = 1.3632e-7
        c14 = -6.1260e-10
        c20 = 3.1260e-5
        c21 = -1.7111e-6
        c22 = 2.5986e-8
        c23 = -2.5353e-10
        c24 = 1.0415e-12
        c30 = -9.7729e-9
        c31 = 3.8513e-10
        c32 = -2.3654e-12

        a00 = 1.389
        a01 = -1.262e-2
        a02 = 7.166e-5
        a03 = 2.008e-6
        a04 = -3.21e-8
        a10 = 9.4742e-5
        a11 = -1.2583e-5
        a12 = -6.4928e-8
        a13 = 1.0515e-8
        a14 = -2.0142e-10
        a20 = -3.9064e-7
        a21 = 9.1061e-9
        a22 = -1.6009e-10
        a23 = 7.994e-12
        a30 = 1.100e-10
        a31 = 6.651e-12
        a32 = -3.391e-13

        b00 = -1.922e-2
        b01 = -4.42e-5
        b10 = 7.3637e-5
        b11 = 1.7950e-7

        d00 = 1.727e-3
        d10 = -7.9836e-6

        dtp = d00 + (d10 * p)

        btp = b00 + b01 * t + (b10 + b11 * t) * p

        atp = (a00 + a01 * t + a02 * t ** 2 + a03 * t ** 3 + a04 * t ** 4) + \
              (a10 + a11 * t + a12 * t ** 2 + a13 * t ** 3 + a14 * t ** 4) * p + \
              (a20 + a21 * t + a22 * t ** 2 + a23 * t ** 3) * p ** 2 + \
              (a30 + a31 * t + a32 * t ** 2) * p ** 3

        cwtp = (c00 + c01 * t + c02 * t ** 2 + c03 * t ** 3 + c04 * t ** 4 + c05 * t ** 5) + \
               (c10 + c11 * t + c12 * t ** 2 + c13 * t ** 3 + c14 * t ** 4) * p + \
               (c20 + c21 * t + c22 * t ** 2 + c23 * t ** 3 + c24 * t ** 4) * p ** 2 + \
               (c30 + c31 * t + c32 * t ** 2) * p ** 3

        return cwtp + atp * s + btp * s ** 1.5 + dtp * s ** 2

    @classmethod
    def sal(cls, d, speed, t, lat=30):
        """Iteratively calculate the salinity based on the speed() method

        Args:
            d: depth in meter
            speed: sound speed in m/sec
            t: temperature in deg Celsius
            lat: latitude in decimal degree

        Returns:  Salinity in PSU (ppt)

        """
        high_value = 50.0
        low_value = 0.0
        num_iterations = 0
        max_iterations = 1e6
        salinity = 0
        speed_calc = 0

        while np.abs(speed_calc - speed) > 0.0005:

            if high_value == low_value:  # unstable sound speed measurement
                logger.warning("found unstable salinity value")
                break
            if num_iterations > max_iterations:
                logger.warning("too many iterations to obtain the salinity value")
                break

            salinity = (high_value + low_value) / 2.0
            speed_calc = cls.speed(d, t, salinity, lat)
            if speed_calc > speed:
                high_value = salinity
            else:
                low_value = salinity

            num_iterations += 1

        return salinity

    @classmethod
    def atg(cls, s, t, p):
        """ Adiabatic temperature gradient

        ref: Fofonoff and Millard(1983)

        Args:
            s: salinity in PSU ppt
            t: temperature in deg Celsius
            p: pressure in dBar

        Returns: adiabatic temperature gradient in deg C/dBar

        """
        a0 = 3.5803E-5
        a1 = 8.5258E-6
        a2 = -6.836E-8
        a3 = 6.6228E-10

        b0 = 1.8932E-6
        b1 = -4.2393E-8

        c0 = 1.8741E-8
        c1 = -6.7795E-10
        c2 = 8.733E-12
        c3 = -5.4481E-14

        d0 = -1.1351E-10
        d1 = 2.7759E-12

        e0 = -4.6206E-13
        e1 = 1.8676E-14
        e2 = -2.1687E-16

        return a0 + (a1 + (a2 + a3 * t) * t) * t + (b0 + b1 * t) * (s - 35) \
               + ((c0 + (c1 + (c2 + c3 * t) * t) * t)
                  + (d0 + d1 * t) * (s - 35)) * p \
               + (e0 + (e1 + e2 * t) * t) * p * p

    @classmethod
    def pot_temp(cls, s, t, p, pr):
        """Compute local potential temperature at pressure

        ref: Fofonoff and Millard(1983)

        Args:
            s: salinity in PSU ppt
            t: temperature
            p: pressure
            pr: reference pressure

        Returns: theta, potential temperature in deg C

        """
        h = pr - p
        xk = h * cls.atg(s=s, t=t, p=p)

        t += + 0.5 * xk
        q = xk
        p += 0.5 * h
        xk = h * cls.atg(s=s, t=t, p=p)

        t += 0.29289322 * (xk - q)
        q = 0.58578644 * xk + 0.121320344 * q
        xk = h * cls.atg(s=s, t=t, p=p)

        t += 1.707106781 * (xk - q)
        q = 3.414213562 * xk - 4.121320344 * q
        p += 0.5 * h
        xk = h * cls.atg(s=s, t=t, p=p)

        return t + (xk - 2.0 * q) / 6.0

    @classmethod
    def in_situ_temp(cls, s, t, p, pr):
        """Compute in-situ temperature at pressure

        Args:
            s: salinity in PSU ppt
            t: temperature
            p: pressure
            pr: reference pressure

        Returns: in-situ temperature in deg C
        """

        if p == pr:
            return t

        temp = t
        new_pot_t = cls.pot_temp(s=s, t=temp, p=p, pr=pr)
        # logger.debug("p: %s, pr: %s" % (p, pr))
        if new_pot_t < t:
            sign = 1
        else:
            sign = -1

        dt = new_pot_t - t
        new_dt = new_pot_t - t

        while abs(new_dt) > 0.001:
            if abs(new_dt) > abs(dt):
                sign = -sign
            temp += sign * 0.001
            new_pot_t = cls.pot_temp(s=s, t=temp, p=p, pr=pr)
            new_dt = new_pot_t - t

        return temp

    @classmethod
    def c2s(cls, c, p, t):
        """Covert conductivity to salinity

        ref: Fofonoff and Millard(1983)

        Args:
            c: conductivity in mmho/cm
            p: pressure in dBar
            t: temperature in deg Celsius

        Returns: Salinity in psu

        """

        e1 = 2.07e-5
        e2 = -6.37e-10
        e3 = 3.989e-15

        d1 = 3.426e-2
        d2 = 4.464e-4
        d3 = 4.215e-1
        d4 = -3.107e-3

        r = c / 42.914
        r1 = p * (e1 + (e2 + e3 * p) * p)
        r2 = 1 + (d1 + d2 * t) * t + (d3 + d4 * t) * r
        rp = 1 + r1 / r2

        c0 = 0.6766097
        c1 = 2.00564e-2
        c2 = 1.104259e-4
        c3 = -6.9698e-7
        c4 = 1.0031e-9

        rt = c0 + (c1 + (c2 + (c3 + c4 * t) * t) * t) * t

        cr = r / (rp * rt)

        return cls.cr2s(cr, t)

    @classmethod
    def cr2s(cls, cr, t):
        """Conductivity ratio to salinity

        Args:
            cr: conductivity ratio
            t: temperature

        Returns: salinity in psu

        """

        a0 = 0.0080
        a1 = -0.1692
        a2 = 25.3851
        a3 = 14.0941
        a4 = -7.0261
        a5 = 2.7081

        b0 = 0.0005
        b1 = -0.0056
        b2 = -0.0066
        b3 = -0.0375
        b4 = 0.0636
        b5 = -0.0144

        k = 0.0162

        rtx = np.sqrt(cr)
        dt = t - 15
        ds = (dt / (1 + k * dt)) * (b0 + (b1 + (b2 + (b3 + (b4 + b5 * rtx) * rtx) * rtx) * rtx) * rtx)

        return a0 + (a1 + (a2 + (a3 + (a4 + a5 * rtx) * rtx) * rtx) * rtx) * rtx + ds

    @classmethod
    def s2c(cls, s, p, t):
        """Calculate conductivity iteratively

        Args:
            s: salinity in psu
            p: pressure in dBar
            t: temperature in deg Celsisu

        Returns: Conductivity mmho/cm
        """

        c = 0
        c_step = 0.1
        max_c = 100

        calc_s = -1
        last_c = c
        last_s = calc_s

        while c < max_c:
            calc_s = cls.c2s(c, p, t)
            # log.debug("%f %f %f %f" % (count, conductivity, calc_salinity, salinity))

            if calc_s > s:
                break

            last_c = c
            last_s = calc_s

            c += c_step

        delta_c = c - last_c
        delta_s = calc_s - last_s

        return last_c + delta_c / delta_s * (s - last_s)

    @classmethod
    def a(cls, f, t, s, d, ph):
        """Calculate attenuation

        ref: Francois and Garrison, J. Acoust. Soc. Am., Vol. 72, No. 6, December 1982

        Args:
            f: frequency in kHz
            t: temperature in deg Celsius
            s: salinity in ppt
            d: depth in meter
            ph: acidity

        Returns: attenuation

        """
        abs_t = 273.0 + t
        c = 1412.0 + 3.21 * t + 1.19 * s + 0.0167 * d  # sound speed calculation

        # Boric Acid Contribution
        a1 = (8.86 / c) * math.pow(10.0, (0.78 * ph - 5.0))
        p1 = 1.0

        f1 = 2.8 * math.pow((s / 35.0), 0.5) * math.pow(10.0, 4.0 - (1245.0 / abs_t))

        # MgSO4 Contribution
        a2 = (21.44 * s / c) * (1.0 + 0.025 * t)
        p2 = (1.0 - 1.37E-4 * d) + (6.2E-9 * d * d)
        f2 = (8.17 * math.pow(10.0, 8.0 - 1990.0 / abs_t)) / (1.0 + 0.0018 * (s - 35.0))

        # Pure Water Contribution
        if t <= 20.0:
            a3 = 4.937E-4 - 2.59E-5 * t + 9.11E-7 * t * t - 1.50E-8 * t * t * t
        else:
            a3 = 3.964E-4 - 1.146E-5 * t + 1.45E-7 * t * t - 6.5E-10 * t * t * t

        p3 = 1.0 - 3.83E-5 * d + 4.9E-10 * d * d

        boric = (a1 * p1 * f1 * f * f) / (f * f + f1 * f1)
        mgso4 = (a2 * p2 * f2 * f * f) / (f * f + f2 * f2)
        h2o = a3 * p3 * f * f

        return boric + mgso4 + h2o

    @classmethod
    def sal2sa(cls, sal, p, lon, lat):
        return gsw.conversions.SA_from_SP(SP=sal, p=p, lon=lon, lat=lat)

    @classmethod
    def t2ct(cls, sa, t, p):
        return gsw.conversions.CT_from_t(SA=sa, t=t, p=p)

    @classmethod
    def geo_strf_dyn_height(cls, sa, ct, p, p_ref):
        try:
            # using new gsw 3.3.0+
            return gsw.geostrophy.geo_strf_dyn_height(sa, ct, p, p_ref, interp_method='linear')
        except:
            # using old gsw 3.0.3
            return cls.geo_strf_dyn_height_gsw303(sa, ct, p, p_ref)

    @classmethod
    def geo_strf_dyn_height_gsw303(cls, sa, ct, p, p_ref):
        """ Calculates dynamic height anomaly.

        Converted from gsw_geo_strf_dyn_height.c by C.Z. HSTB in Nov 2015
        """

        def p_sequence(p1, p2, i_max_dp, p_seq):
            d_p = p2 - p1
            n = int(np.ceil(d_p / i_max_dp))
            pstep = d_p / n if n != 0 else 0

            n_ps = n
            for j in range(n):
                p_seq[j] = p1 + pstep * (j + 1)

            return n_ps

        max_dp_i = 1.0
        nz = len(sa)
        dp = p[1:nz] - p[0:nz - 1]
        dp_min = np.min(dp)
        dp_max = np.max(dp)
        if dp_min <= 0 or np.min(p) < 0:
            # print(dp)
            logger.warning("dp_min: %s, p min: %d" % (dp_min, np.min(p)))
            raise RuntimeError('pressure must be monotonic and non negative')
        p_min = p[0]
        p_max = p[-1]
        if p_ref > p_max:
            raise RuntimeError('the reference pressure p_ref is deeper than all bottles')

        # Determine if there is a "bottle" at exactly p_ref
        ip_ref = -1
        for i in range(nz):
            if p[i] == p_ref:
                ip_ref = i
                break

        dyn_height = np.zeros(nz)
        if (dp_max <= max_dp_i) and (p[0] == 0.0) and (ip_ref >= 0):

            # vertical resolution is good (bottle gap is no larger than max_dp_i)
            # & the vertical profile begins at the surface (i.e. at p = 0 dbar)
            # & the profile contains a "bottle" at exactly p_ref.
            # "geo_strf_dyn_height0" is the dynamic height anomaly with respect to p_ref = 0 (the surface).
            b = gsw.density_enthalpy_48.specvol_anom(sa, ct, p)
            geo_strf_dyn_height0 = np.zeros(nz)

            for i in range(nz)[1:]:
                b_av = 0.5 * (b[i] + b[i - 1])
                geo_strf_dyn_height0[i] = b_av * dp[i - 1] * 1e4

            for i in range(nz)[1:]:  # cumulative sum
                geo_strf_dyn_height0[i] = geo_strf_dyn_height0[i - 1] - geo_strf_dyn_height0[i]

            for i in range(nz):
                dyn_height[i] = geo_strf_dyn_height0[i] - geo_strf_dyn_height0[ip_ref]

        else:
            # Test if there are vertical gaps between adjacent "bottles" which are
            # greater than max_dp_i, and that there is a "bottle" exactly at the
            # reference pressure.
            ii_data = np.zeros(nz + 1)
            i_bpr = 0  # initialize
            if (dp_max <= max_dp_i) and (ip_ref >= 0):

                # Vertical resolution is already good (no larger than max_dp_i), and
                # there is a "bottle" at exactly p_ref.
                if p_min > 0.0:
                    # resolution is fine and there is a bottle at p_ref, but
                    # there is not a bottle at p = 0. So add an extra bottle.
                    sa_i = np.concatenate([[sa[0]], sa])
                    ct_i = np.concatenate([[ct[0]], ct])
                    p_i = np.concatenate([[0], p])
                    i_bpr = ip_ref + 1

                else:
                    # resolution is fine, there is a bottle at p_ref, and
                    # there is a bottle at p = 0
                    sa_i = sa
                    ct_i = ct
                    p_i = p
                    i_bpr = ip_ref

                p_cnt = len(p_i)
                for i in range(p_cnt):
                    ii_data[i] = i
            else:
                # interpolation is needed.
                np_max = len(p) + 2 * int(p[-1] / max_dp_i + 0.5)
                p_i = np.zeros(np_max)

                if p_min > 0.0:

                    # there is not a bottle at p = 0.
                    if p_ref < p_min:
                        # p_ref is shallower than the minimum bottle pressure.
                        p_i[0] = 0.0
                        nps = p_sequence(p_i[0], p_ref, max_dp_i, p_i[1:])
                        i_bpr = p_cnt = nps
                        p_cnt += 1
                        nps = p_sequence(p_ref, p_min, max_dp_i, p_i[p_cnt:])
                        p_cnt += nps

                    else:
                        # p_ref is deeper than the minimum bottle pressure.
                        p_i[0] = 0.0
                        p_i[1] = p_min
                        p_cnt = 2

                else:
                    # there is a bottle at p = 0.
                    p_i[0] = p_min
                    p_cnt = 1

                for i_bottle in range(nz - 1):

                    ii_data[i_bottle] = p_cnt - 1
                    if p[i_bottle] == p_ref:
                        i_bpr = p_cnt - 1

                    if p[i_bottle] < p_ref < p[i_bottle + 1]:
                        # ... reference pressure is spanned by bottle pairs -
                        # need to include p_ref as an interpolated pressure.
                        nps = p_sequence(p[i_bottle], p_ref, max_dp_i, p_i[p_cnt:])
                        p_cnt += nps
                        i_bpr = p_cnt - 1
                        nps = p_sequence(p_ref, p[i_bottle + 1], max_dp_i, p_i[p_cnt:])
                        p_cnt += nps

                    else:
                        # ... reference pressure is not spanned by bottle pairs.
                        nps = p_sequence(p[i_bottle], p[i_bottle + 1], max_dp_i, p_i[p_cnt:])
                        p_cnt += nps

                ii_data[nz - 1] = p_cnt - 1
                if p[nz - 1] == p_ref:
                    i_bpr = p_cnt - 1

                p_i = p_i[:p_cnt]
                p_i[-1] = p[-1]
                if p[0] <= 0:
                    sa_i, ct_i = gsw.library.interp_SA_CT(sa, ct, p, p_i)

                else:
                    sa_i, ct_i = gsw.library.interp_SA_CT(np.concatenate([[sa[0]], sa]), np.concatenate([[ct[0]], ct]),
                                                          np.concatenate([[0], p]), p_i)
                    # return Si[:p_cnt], Ti[:p_cnt], p_i[:p_cnt]
            b = gsw.density_enthalpy_48.specvol_anom(sa_i, ct_i, p_i)
            # "geo_strf_dyn_height0" is the dynamic height anomaly with respect to p_ref = 0 (the surface).
            geo_strf_dyn_height0 = np.zeros(p_cnt)

            for i in range(p_cnt)[1:]:
                b_av = 0.5 * (b[i] + b[i - 1])
                dp_i = p_i[i] - p_i[i - 1]
                geo_strf_dyn_height0[i] = b_av * dp_i

            for i in range(p_cnt)[1:]:  # cumulative sum
                geo_strf_dyn_height0[i] = geo_strf_dyn_height0[i - 1] - geo_strf_dyn_height0[i]

            for i in range(nz):
                dyn_height[i] = (geo_strf_dyn_height0[int(ii_data[i])] - geo_strf_dyn_height0[i_bpr]) * 1e4

        return dyn_height

    @classmethod
    def attenuation(cls, f, t, s, d, ph):
        # Francois & Garrison, J. Acoust. Soc. Am., Vol. 72, No. 6, December 1982
        # f frequency (kHz)
        # T Temperature (degC)
        # S Salinity (ppt)
        # D Depth (m)
        # pH Acidity
        abs_temp = 273.0 + t

        # sound speed calculation
        c = 1412.0 + 3.21 * t + 1.19 * s + 0.0167 * d

        # Boric Acid Contribution
        A1 = (8.86 / c) * math.pow(10.0, (0.78 * ph - 5.0))
        P1 = 1.0

        f1 = 2.8 * math.pow((s / 35.0), 0.5) * math.pow(10.0, 4.0 - (1245.0 / abs_temp))

        # MgSO4 Contribution
        A2 = (21.44 * s / c) * (1.0 + 0.025 * t)
        P2 = (1.0 - 1.37E-4 * d) + (6.2E-9 * d * d)
        f2 = (8.17 * math.pow(10.0, 8.0 - 1990.0 / abs_temp)) / (1.0 + 0.0018 * (s - 35.0))

        # Pure Water Contribution
        if t <= 20.0:
            A3 = 4.937E-4 - 2.59E-5 * t + 9.11E-7 * t * t - 1.50E-8 * t * t * t
        else:
            A3 = 3.964E-4 - 1.146E-5 * t + 1.45E-7 * t * t - 6.5E-10 * t * t * t

        P3 = 1.0 - 3.83E-5 * d + 4.9E-10 * d * d

        boric = (A1 * P1 * f1 * f * f) / (f * f + f1 * f1)
        magnes = (A2 * P2 * f2 * f * f) / (f * f + f2 * f2)
        purewat = A3 * P3 * f * f

        atten = boric + magnes + purewat

        return atten
