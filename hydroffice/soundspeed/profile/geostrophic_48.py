# -*- coding: utf-8 -*-

from __future__ import division

import numpy as np
import gsw
import logging
from .oceanography import Oceanography as Oc

logger = logging.getLogger(__name__)


def geo_strf_dyn_height(SA,CT,p,p_ref):
    """
    !==========================================================================
    !  Calculates dynamic height anomaly as the integral of specific volume
    !  anomaly from the pressure p of the bottle to the reference pressure
    !  p_ref.
    !
    !  Hence, geo_strf_dyn_height is the dynamic height anomaly with respect
    !  to a given reference pressure.  This is the geostrophic streamfunction 
    !  for the difference between the horizontal velocity at the pressure 
    !  concerned, p, and the horizontal velocity at p_ref.  Dynamic height 
    !  anomaly is the geostrophic streamfunction in an isobaric surface.  The 
    !  reference values used for the specific volume anomaly are 
    !  SSO = 35.16504 g/kg and CT = 0 deg C.  This function calculates 
    !  specific volume anomaly using the computationally efficient 
    !  expression for specific volume of Roquet et al. (2015). 
    !
    !  This function evaluates the pressure integral of specific volume using 
    !  SA and CT interpolated with respect to pressure using the method of 
    !  Reiniger and Ross (1968).  It uses a weighted mean of (i) values 
    !  obtained from linear interpolation of the two nearest data points, and 
    !  (ii) a linear extrapolation of the pairs of data above and below.  This 
    !  "curve fitting" method resembles the use of cubic splines.  
    !
    !  SA    =  Absolute Salinity                                      [ g/kg ]
    !  CT    =  Conservative Temperature (ITS-90)                     [ deg C ]
    !  p     =  sea pressure                                           [ dbar ]
    !           ( i.e. absolute pressure - 10.1325 dbar )
    !  p_ref =  reference pressure                                     [ dbar ]
    !           ( i.e. reference absolute pressure - 10.1325 dbar )
    !
    !  geo_strf_dyn_height  =  dynamic height anomaly               [ m^2/s^2 ]
    !   Note. If p_ref exceeds the pressure of the deepest bottle on a 
    !     vertical profile, the dynamic height anomaly for each bottle 
    !     on the whole vertical profile is returned as NaN.
    !========================================================================== 
    This is converted from gsw_geo_strf_dyn_height.c by C.Z. HSTB in Nov 2015
    """
    max_dp_i = 1.0
    nz = len(SA)
    dp = p[1:nz] - p[0:nz-1]
    dp_min = np.min(dp)
    dp_max = np.max(dp)
    if dp_min <= 0 or np.min(p) < 0:
        print 'Error: pressure must be monotonic and non negative'
        return None
    p_min = p[0]
    p_max = p[-1]
    if p_ref > p_max:
        print 'Error: the reference pressure p_ref is deeper than all bottles'
        return None
    # Determine if there is a "bottle" at exactly p_ref
    ipref = -1;
    for i in xrange(nz):
        if p[i] == p_ref:
            ipref = i
            break

    dyn_height = np.zeros(nz)
    if ((dp_max <= max_dp_i) and (p[0] == 0.0) and (ipref >= 0)):
        # vertical resolution is good (bottle gap is no larger than max_dp_i)
        # & the vertical profile begins at the surface (i.e. at p = 0 dbar)
        # & the profile contains a "bottle" at exactly p_ref.
        # "geo_strf_dyn_height0" is the dynamic height anomaly with respect to p_ref = 0 (the surface).
        b = gsw.density_enthalpy_48.specvol_anom(SA,CT,p)
        geo_strf_dyn_height0 = np.zeros(nz)
        for i in range(nz)[1:]:
            b_av = 0.5*(b[i] + b[i-1])
            geo_strf_dyn_height0[i] = b_av*dp[i-1]*1e4
        for i in range(nz)[1:]:  #cumulative sum
            geo_strf_dyn_height0[i] = geo_strf_dyn_height0[i-1] - geo_strf_dyn_height0[i]
        for i in xrange(nz):
            dyn_height[i] = geo_strf_dyn_height0[i] - geo_strf_dyn_height0[ipref]
    else:
        # Test if there are vertical gaps between adjacent "bottles" which are
        # greater than max_dp_i, and that there is a "bottle" exactly at the
        # reference pressure.        
        iidata = np.zeros(nz+1)
        if ((dp_max <= max_dp_i) and (ipref >= 0)):
            # Vertical resolution is already good (no larger than max_dp_i), and
            # there is a "bottle" at exactly p_ref.
            if (p_min > 0.0):
                # resolution is fine and there is a bottle at p_ref, but
                # there is not a bottle at p = 0. So add an extra bottle.
                sa_i = np.concatenate([[SA[0]], SA])
                ct_i = np.concatenate([[CT[0]], CT])
                p_i = np.concatenate([[0], p])
                ibpr = ipref+1
            else:
                # resolution is fine, there is a bottle at p_ref, and
                # there is a bottle at p = 0
                sa_i = SA
                ct_i = CT
                p_i = p
                ibpr = ipref
            p_cnt = len(p_i)
            for i in xrange(p_cnt):
                iidata[i] = i
        else:
            # interpolation is needed.
            np_max = len(p) + 2*int(p[-1]/max_dp_i+0.5)
            p_i = np.zeros(np_max)
            if (p_min > 0.0):
                # there is not a bottle at p = 0.
                if (p_ref < p_min):
                    # p_ref is shallower than the minimum bottle pressure.
                    p_i[0] = 0.0
                    nps = p_sequence(p_i[0],p_ref,max_dp_i, p_i[1:])
                    ibpr = p_cnt = nps
                    p_cnt += 1
                    nps = p_sequence(p_ref,p_min,max_dp_i, p_i[p_cnt:])
                    p_cnt += nps
                    top_pad = p_cnt
                else:
                    # p_ref is deeper than the minimum bottle pressure.
                    p_i[0] = 0.0
                    p_i[1] = p_min
                    top_pad = 2
                    p_cnt = 2
            else:
                # there is a bottle at p = 0.
                p_i[0] = p_min
                top_pad = 1
                p_cnt = 1
                
            for ibottle in xrange(nz-1):
                iidata[ibottle] = p_cnt-1
                if (p[ibottle] == p_ref): ibpr = p_cnt-1
                if (p[ibottle] < p_ref and p[ibottle+1] > p_ref):
                    # ... reference pressure is spanned by bottle pairs -
                    # need to include p_ref as an interpolated pressure.
                    nps = p_sequence(p[ibottle],p_ref,max_dp_i, p_i[p_cnt:])
                    p_cnt += nps
                    ibpr = p_cnt-1
                    nps = p_sequence(p_ref,p[ibottle+1],max_dp_i,p_i[p_cnt:])
                    p_cnt += nps
                else:
                    # ... reference pressure is not spanned by bottle pairs.
                    nps = p_sequence(p[ibottle],p[ibottle+1],max_dp_i,p_i[p_cnt:])
                    p_cnt += nps
            iidata[nz-1] = p_cnt-1
            if (p[nz-1] == p_ref): ibpr = p_cnt-1
            
            p_i = p_i[:p_cnt]
            p_i[-1] = p[-1]
            if p[0] <= 0:
                sa_i, ct_i = gsw.library.interp_SA_CT(SA, CT, p, p_i)
            else:
                sa_i, ct_i = gsw.library.interp_SA_CT(np.concatenate([[SA[0]], SA]), np.concatenate([[CT[0]], CT]), np.concatenate([[0], p]), p_i)
            #return Si[:p_cnt], Ti[:p_cnt], p_i[:p_cnt]
        b = gsw.density_enthalpy_48.specvol_anom(sa_i,ct_i,p_i)
        # "geo_strf_dyn_height0" is the dynamic height anomaly with respect to p_ref = 0 (the surface).
        geo_strf_dyn_height0 = np.zeros(p_cnt)
        for i in range(p_cnt)[1:]:
            b_av = 0.5*(b[i] + b[i-1])
            dp_i = p_i[i]-p_i[i-1]
            geo_strf_dyn_height0[i] = b_av*dp_i
        for i in range(p_cnt)[1:]:  #cumulative sum
            geo_strf_dyn_height0[i] = geo_strf_dyn_height0[i-1] - geo_strf_dyn_height0[i]
        for i in xrange(nz):
            dyn_height[i] = (geo_strf_dyn_height0[iidata[i]] - geo_strf_dyn_height0[ibpr])*1e4
    return dyn_height

def p_sequence(p1, p2, max_dp_i, pseq):
    """Converted from gsw_geo_strf_dyn_height.c by C.Z. HSTB in Nov 2015"""
    dp = p2 - p1
    n = int(np.ceil(dp/max_dp_i))
    pstep = dp/n if n!=0 else 0
    
    nps = n
    for i in xrange(n):
        pseq[i] = p1+pstep*(i+1)
    return nps

def d_from_p(pro):
    """Convert pressure to depth for a given pro (profile object)"""
    num = pro.data.num_samples
    p = pro.data.press[:num]
    t = pro.data.temp[:num]
    SP = pro.data.sal[:num]
    
    if not pro.meta.latitude:
        lat = 30.0
        logger.warning("using default latitude: %s" % lat)
    else:
        lat = pro.meta.latitude    
    
    if t.min() == t.max() or SP.min() == SP.max():
        # temperature and/or salinity is not available
        error = True
    else:
        error = False
        try:
            if not pro.meta.longitude:
                lon = -70.0
                logger.warning("using default longitude: %s" % lon)
            else:
                lon = pro.meta.longitude
            SA = gsw.conversions.SA_from_SP(SP, p, lon, lat)
            CT = gsw.conversions.CT_from_t(SA, t, p)
            dyn = geo_strf_dyn_height(SA, CT, p, p_ref=0)
            depth = -gsw.conversions.z_from_p(p, lat, geo_strf_dyn_height=dyn)
            for d in depth:
                if np.isnan(d):
                    error = True
                    logger.warning("error in geo_strf_dyn_height") 
                    break    
        except:
            error = True
            logger.warning("error in gsw lib") 
    
    if error:
        for count in range(num):
            pro.data.depth[count] = Oc.p2d(p=pro.data.pressure[count], lat=lat) 
    else:
        for count in range(num):
            pro.data.depth[count] = depth[count]        


