from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
import logging
import os

logger = logging.getLogger(__name__)


class Oceanography(object):
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

    @classmethod
    def p2d(cls, p, lat=30.0):
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
    def d2p(cls, d, lat=30.0):
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

        p = cls.d2p(d, lat) / 10  # pressure in bar

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
