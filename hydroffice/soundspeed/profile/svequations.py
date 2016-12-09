from __future__ import absolute_import, division, print_function, unicode_literals

import numpy as np
from numpy import sin, cos, tan, arcsin, log, arctan, exp, sqrt
import logging

logger = logging.getLogger(__name__)


class SVEquations(object):
    
    @classmethod
    def GetSVPLayerParameters(cls, LaunchAngleRadians, Layers):
        try:
            import SV_ext #import the C (scipy.weave) extension, if possible
            return cls.GetSVPLayerParameters_fast(LaunchAngleRadians, Layers)
        except ImportError:
            try:
                cls.build_SV()
                import SV_ext
                return cls.GetSVPLayerParameters_fast(LaunchAngleRadians, Layers)
            except:
                return cls.GetSVPLayerParameters_slow(LaunchAngleRadians, Layers)

    @classmethod
    def build_SV(cls):
        """ Builds an extension module with SV computations.
        """
        mod = ext_tools.ext_module('SV_ext')
        # this is effectively a type declaration so the compiler knows what the types are
        #TriangleToNodes=NodeToTriangles=scipy.zeros([8,2],scipy.int32)
        nLenLayers = 10
        LaunchAngleRadians = float(10.0)
        arr = {}
        arr['double'] = np.zeros([10,2], np.float64) #array to hold normal computed for each triangle
        arr['float'] = np.zeros([10,2], np.float32) #array to hold normal computed for each triangle
        
        for dtype in ['double']: #, 'float' -- only doubles for SV #loop the supported types for the xyz positions and normal vectors -- basically a macro or template
            depth= deltadepth=speed= gradient= gamma= radius= totaltime= totalrange=arr[dtype] #set variables up as proper type for this incarnation
            fib_code = """ 
                            int SVPParams_dtype(double LaunchAngleRadians, int nLenLayers, //len(Layers)
                                                     dtype *depth, dtype *speed, dtype *deltadepth, dtype *gradient, //input arrays 
                                                     dtype *gamma, dtype *radius, dtype *totaltime, dtype *totalrange //output variables
                                                    )
                            {
                                int j;
                            
                                gamma[0]=LaunchAngleRadians;
                                totaltime[0]=0;
                                totalrange[0]=0;
    
                                for(j=0; j<nLenLayers-1; j++){
                                    gamma[j+1]=asin((speed[j+1]/speed[j])*sin(gamma[j]));
                                    if(gamma[j]==0){ // nadir beam (could cause division by zero errors below)
                                        radius[j]=0;
                                        totaltime[j+1] =totaltime[j] +(deltadepth[j])/((speed[j+1]+speed[j])/2.0);
                                        totalrange[j+1]=totalrange[j];
                                    }
                                    else if(gradient[j]==0){ 
                                        radius[j]=0;
                                        totaltime[j+1] =totaltime[j] +(deltadepth[j])/(speed[j]*cos(gamma[j]));
                                        totalrange[j+1]=totalrange[j]+(deltadepth[j])*tan(gamma[j]);
                                    }
                                    else{
                                        radius[j]=speed[j]/(gradient[j]*sin(gamma[j]));
                                        totaltime[j+1]=totaltime[j]+log(tan(gamma[j+1]/2.0)/tan(gamma[j]/2.0))/gradient[j];
                                        totalrange[j+1]=totalrange[j]+radius[j]*(cos(gamma[j])-cos(gamma[j+1]));
                                    }
                                }
                                return 0; //success
                            }
                    """
            ext_code = """
                           return_val = SVPParams_dtype(LaunchAngleRadians,  nLenLayers,
                                                    depth, speed,  deltadepth, gradient, 
                                                    gamma, radius, totaltime, totalrange);
                       """
            fib = ext_tools.ext_function('SVPParameters_'+dtype,ext_code.replace('dtype', dtype),
                                         [ 'LaunchAngleRadians',  'nLenLayers',
                                                      'depth', 'speed',  'deltadepth', 'gradient', 
                                                      'gamma', 'radius', 'totaltime', 'totalrange' ])
            fib.customize.add_support_code(fib_code.replace('dtype', dtype))
            mod.add_function(fib)
    
        mod.compile() #compile for all the supported types of scipy arrays

    @classmethod
    def GetSVPLayerParameters_fast(cls, LaunchAngleRadians, Layers):
        ''' Layers is either a record array with 'depth' and 'soundspeed' columns 
            or is a scipy array with depth as first column and speed as second column
            Should be sorted by depth first without repeating depths (will raise division by zero)
            Assumes that the layers start at the transducer at Zero depth 
        '''
        #nLayers=len(Layers)
        for a in ('gradient', 'gamma', 'radius', 'totaltime', 'totalrange'):
            exec a+"= np.zeros(Layers.shape, np.float64)"
        try:
            speed = Layers['speed']
        except:
            speed = [r[1] for r in Layers]
        try:
            depth = Layers['depth']
        except:
            depth = [r[0] for r in Layers]
        speed = np.array(speed, np.float64) #need double precision for this computation
        depth = np.array(depth, np.float64)
        
        depth[0] = 0.0 #assume zero for top layer -- say first two measurements were 1m and 2m respectively, we are making the first layer go from 0m to 2m.
        
        deltadepth = np.diff(depth)
        gradient = np.diff(speed) / deltadepth
    
        retval = SV_ext.SVPParameters_double(float(LaunchAngleRadians),  len(Layers),
                                                      depth, speed,  deltadepth, gradient, 
                                                      gamma, radius, totaltime, totalrange)
        return gradient, gamma, radius, totaltime, totalrange

    @classmethod
    def GetSVPLayerParameters_slow(cls, LaunchAngleRadians, Layers):
        ''' Layers is either a record array with 'depth' and 'soundspeed' columns 
            or is a scipy array with depth as first column and speed as second column
            Should be sorted by depth first without repeating depths (will raise division by zero)
            Assumes that the layers start at the transducer at Zero depth 
        '''
        #nLayers=len(Layers)
        for a in ('gradient', 'gamma', 'radius', 'totaltime', 'totalrange'):
            exec a+"= np.zeros(Layers.shape, np.float64)"
        try:
            speed = Layers['speed']
        except:
            speed = [r[1] for r in Layers]
        try:
            depth = Layers['depth']
        except:
            depth = [r[0] for r in Layers]
        speed = np.array(speed, np.float64) #need double precision for this computation
        depth = np.array(depth, np.float64)
        
        depth[0] = 0.0 #assume zero for top layer -- say first two measurements were 1m and 2m respectively, we are making the first layer go from 0m to 2m.
        
        gamma[0] = LaunchAngleRadians
        totaltime[0] = 0
        totalrange[0] = 0
    
        deltadepth = np.diff(depth)
        gradient = np.diff(speed) / deltadepth
        for j in range(len(Layers) - 1):
            gamma[j+1]=arcsin((speed[j+1]/speed[j])*sin(gamma[j]))
            if(gamma[j]==0): #// nadir beam (could cause division by zero errors below)
                radius[j]=0
                totaltime[j+1] =totaltime[j] +(deltadepth[j])/((speed[j+1]+speed[j])/2.0)
                totalrange[j+1]=totalrange[j]
            elif(gradient[j]==0): 
                radius[j]=0
                totaltime[j+1] =totaltime[j] +(deltadepth[j])/(speed[j]*cos(gamma[j]))
                totalrange[j+1]=totalrange[j]+(deltadepth[j])*tan(gamma[j])
            else:
                radius[j]=speed[j]/(gradient[j]*sin(gamma[j]))
                totaltime[j+1]=totaltime[j]+log(tan(gamma[j+1]/2.0)/tan(gamma[j]/2.0))/gradient[j]
                totalrange[j+1]=totalrange[j]+radius[j]*(cos(gamma[j])-cos(gamma[j+1]))
        #Note the last radius doen't get computed but that isn't important
        #we always want to be in the last layer, so we use the comptutations at the next to last layer
        #and interpolate to the depth/time which is before the end of the last layer
        return gradient, gamma, radius, totaltime, totalrange

    @classmethod
    def RayTraceUsingParameters(cls, traveltimes, Layers, params, bProject=False):
        ''' Traveltime must end within the measured layers (or returns false). To protect against failure, user can pad 
            a final layer very deep with the same SV as the last true measurement.
            
            Layers is either a record array with 'depth' and 'soundspeed' columns 
            or is a scipy array with depth as first column and speed as second column
            Should be sorted by depth first without repeating depths (will raise division by zero)    
            
            Assumes that the layers start at the transducer at Zero depth     
            Will return a scipy array of the depth,horizontal_distances where -1,-1 denotes an out of range traveltime
            bProject should extend the cat to infinity, most useful for the scipy.optimize.fsolve that needs a continuous function
        '''
        nLayers = len(Layers) - 1;
        try:
            speed = Layers['speed']
        except:
            speed = [r[1] for r in Layers]
        try:
            depth = Layers['depth'].copy()
        except:
            depth = [r[0] for r in Layers]
        depth[0] = 0.0 #assume zero for top layer -- say first two measurements were 1m and 2m respectively, we are making the first layer go from 0m to 2m.
        
        gradient, gamma, radius, totaltime, totalrange = params
        try:
            len(traveltimes) #make sure we get a list of indices back to iterate on -- even if only one traveltime sent
        except:
            traveltimes = [traveltimes]
        nEndLayers = totaltime.searchsorted(traveltimes) - 1
        ret = np.zeros([len(traveltimes), 2]) - 1.0 #create an array where -1 denotes out of range
        for ind, nEndLayer in enumerate(nEndLayers):
            if nEndLayer == -1:
                nEndLayer = 0
            if nEndLayer < nLayers or bProject: #SVP deep enough
                tau=traveltimes[ind]-totaltime[nEndLayer]
                #Note the last radius doen't get computed but that isn't important
                #we always want to be in the last layer, so we use the comptutations at the next to last layer
                #and interpolate to the depth/time which is before the end of the last layer
                if(radius[nEndLayer]==0):
                    if nEndLayer < nLayers:
                        a1 = totaltime[nEndLayer]
                        a2 = totaltime[nEndLayer+1]
                        a3 = speed[nEndLayer]
                        a4 = speed[nEndLayer+1]
                        if isinstance(a1, np.ndarray):
                            a1 = a1[0]
                            a2 = a2[0]
                            a3 = a3[0]
                            a4 = a4[0]
                        endspeed = np.interp(traveltimes[ind], [a1,a2], [a3,a4])
                        #endspeed = scipy.interp(traveltimes[ind], [totaltime[nEndLayer],totaltime[nEndLayer+1]], [speed[nEndLayer],speed[nEndLayer+1]])
                    else: #projecting the last speed to infinite depth
                        endspeed = speed[nEndLayer] 
                    avgspeed = (speed[nEndLayer]+endspeed)/2.0
                    finaldepth=avgspeed*tau*cos(gamma[nEndLayer])+depth[nEndLayer]
                    finalrange=avgspeed*tau*sin(gamma[nEndLayer])+totalrange[nEndLayer]
                else:
                    finaldepth=radius[nEndLayer]*( sin(2*arctan(tan(gamma[nEndLayer]/2.0)*exp(gradient[nEndLayer]*tau)))-sin(gamma[nEndLayer])) + depth[nEndLayer]
                    finalrange=radius[nEndLayer]*(-cos(2*arctan(tan(gamma[nEndLayer]/2.0)*exp(gradient[nEndLayer]*tau)))+cos(gamma[nEndLayer])) + totalrange[nEndLayer]
                #this would translate to acrosstrack, alongtrack components if we passed in pitch, roll, launchangle
                #result[0]=finalrange*LaunchVector[0]/sqrt(LaunchVector[1]*LaunchVector[1]+LaunchVector[0]*LaunchVector[0])
                #result[1]=finalrange*LaunchVector[1]/sqrt(LaunchVector[1]*LaunchVector[1]+LaunchVector[0]*LaunchVector[0])
                #result[2]=finaldepth
                if isinstance(finaldepth, np.ndarray):
                    finaldepth = finaldepth[0]
                    finalrange = finalrange[0]
                ret[ind] = (finaldepth, finalrange)
        return ret

