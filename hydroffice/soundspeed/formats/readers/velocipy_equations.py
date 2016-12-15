import numpy
from numpy import power as pow
import numpy as np

from hydroffice.soundspeed.formats.readers import sbe_constants

coefficients = '''
C00 	1402.388 	A02 	7.166E-5
C01 	5.03830 	A03 	2.008E-6
C02 	-5.81090E-2 	A04 	-3.21E-8
C03 	3.3432E-4 	A10 	9.4742E-5
C04 	-1.47797E-6 	A11 	-1.2583E-5
C05 	3.1419E-9 	A12 	-6.4928E-8
C10 	0.153563 	A13 	1.0515E-8
C11 	6.8999E-4 	A14 	-2.0142E-10
C12 	-8.1829E-6 	A20 	-3.9064E-7
C13 	1.3632E-7 	A21 	9.1061E-9
C14 	-6.1260E-10 	A22 	-1.6009E-10
C20 	3.1260E-5 	A23 	7.994E-12
C21 	-1.7111E-6 	A30 	1.100E-10
C22 	2.5986E-8 	A31 	6.651E-12
C23 	-2.5353E-10 	A32 	-3.391E-13
C24 	1.0415E-12 	B00 	-1.922E-2
C30 	-9.7729E-9 	B01 	-4.42E-5
C31 	3.8513E-10 	B10 	7.3637E-5
C32 	-2.3654E-12 	B11 	1.7950E-7
A00 	1.389 	D00 	1.727E-3
A01 	-1.262E-2 	D10 	-7.9836E-6
'''

# from http://resource.npl.co.uk/acoustics/techguides/soundseawater/content.html
doc = '''
c(S,T,P) =      Cw(T,P) + A(T,P)S + B(T,P)S3/2 + D(T,P)S2
 
Cw(T,P) = 	(C00 + C01T + C02T2 + C03T3 + C04T4 + C05T5) +
                (C10 + C11T + C12T2 + C13T3 + C14T4)P +
                (C20 +C21T +C22T2 + C23T3 + C24T4)P2 +
                (C30 + C31T + C32T2)P3
              
A(T,P) =   	(A00 + A01T + A02T2 + A03T3 + A04T4) +
                (A10 + A11T + A12T2 + A13T3 + A14T4)P +
                (A20 + A21T + A22T2 + A23T3)P2 +
                (A30 + A31T + A32T2)P3
                           
B(T,P) = 	B00 + B01T + (B10 + B11T)P

D(T,P) = 	D00 + D10P

T = temperature in degrees Celsius
S = salinity in Practical Salinity Units (parts per thousand)
P = pressure in bar

Range of validity: temperature 0 to 40 ?C, salinity 0 to 40 parts per thousand, pressure 0 to 1000 bar (Wong and Zhu, 1995).
'''

# Load all the coefficients
all = coefficients.split()
while True:
  try:
    val, var = all.pop(), all.pop()
  except IndexError: break
  s =  "%s = %s" % (var, val)
  exec(s)

def ChenMillero(T, S, P):
  ''' T is temperature in degrees C
      S in salinity in parts per thousand
      P is pressure in decibars
      returned sound speed is in m/s
  '''
  try:
      if min(T) < 0. or max(T) > 40.:
        raise ValueError("Chen-Millero equation is only valid with temperature ranging: 0 < T < 40 degrees celcius (%.02f, %0.2f given)" % (min(T), max(T)))
  except TypeError: #raised if is float/int type
      if T < 0. or T > 40.:
        raise ValueError("Chen-Millero equation is only valid with temperature ranging: 0 < T < 40 degrees celcius (%.02f given)" % T)
  try:
      if min(S) < 0. or max(S) > 40.:
        raise ValueError("Chen-Millero equation is only valid with salinity ranging: 0 < S < 40 PSU (parts per thousand) (%.02f, %0.2f given)" % (min(S), max(S)))
  except TypeError: #raised if is float/int type
      if S < 0. or S > 40.:
        raise ValueError("Chen-Millero equation is only valid with salinity ranging: 0 < S < 40 PSU (parts per thousand) (%.02f given)" % S)
  try:
    if min(P) < 0. or max(P) > 10000.:
      raise ValueError("Chen-Millero equation is only valid with pressure ranging: 0 < P < 10000 decibar (%.02f, %0.2f given)" % (min(P), max(P)))
  except TypeError: #raised if is float/int type
    if P < 0. or P > 10000.:
      raise ValueError("Chen-Millero equation is only valid with pressure ranging: 0 < P < 10000 decibar (%.02f given)" % P)
  return _ChenMillero(T, S, P)
  
def _ChenMillero(T, S, P): 
  '''No checks on input!!!
  '''
  P=P/10.0 #Equations are in Bars, convert from decibars
  return Cw(T, P) + A(T, P) * S + B(T, P) * pow(S, 1.5) + D(T, P) * S * S

def Cw(T, P):
  T3 = numpy.power(T, 3)
  T2 = numpy.power(T, 2)
  T4 = numpy.power(T, 4)
  return (C00 + C01 * T + C02 * T2 + C03 * T3 + C04 * T4 + C05 * pow(T, 5)) + \
         (C10 + C11 * T + C12 * T2 + C13 * T3 + C14 * T4 ) * P + \
         (C20 + C21 * T + C22 * T2 + C23 * T3 + C24 * T4 ) * P * P + \
         (C30 + C31 * T + C32 * T2) * pow(P, 3)

def A(T, P):
  T3 = numpy.power(T, 3)
  T2 = numpy.power(T, 2)
  T4 = numpy.power(T, 4)
  return (A00 + A01 * T + A02 * T2 + A03 * T3 + A04 * T4 ) + \
         (A10 + A11 * T + A12 * T2 + A13 * T3 + A14 * T4 ) * P + \
         (A20 + A21 * T + A22 * T2 + A23 * T3) * P * P + \
         (A30 + A31 * T + A32 * T2) * pow(P, 3)

def B(T, P):
  return B00 + B01 * T + (B10 + B11 * T) * P 

def D(T, P):
  return D00 + D10 * P

def ChenMillero_VelocWin(T, S, PO):
    '''
    ' Sound Speed Seawater Chen and Millero 1977,JASA,62,1129-35
    
    ' This function was downloaded from the following web site:
    ' http://ihttp://ioc.unesco.org/oceanteacher/resourcekit/M3/Classroom/Tutorials/Processing/CTDDataProcess.htmoc.unesco.org/oceanteacher/resourcekit/M3/Classroom/Tutorials/Processing/CTDDataProcess.htm
    
    ' units:
    ' pressure PO decibars
    ' temperature T deg celsius (IPTS-68)
    ' salinity S (PSS-78)
    
    ' sound speed SVEL meters/second
    
    ' checkvalue:SVEL=1731,995m/s,S=40(PSS-78),T=40degC,P=10000db
    ' ***********************************************
    ' TEST
    ' checkvalue:SVEL=1731,995m/s,S=40(PSS-78),T=40degC,P=10000db
    ' Dim sv As Single
    ' sv = SVEL(40, 40, 10000)
    ' ************************************************
    '''
      
    #' scale pressure to bars
    p = PO / 10#
    sr = numpy.sqrt(S if S>0 else 0)
    #' S**2 term
    D = 0.001727 - 0.0000079836 * p
    #' S**3/2 term
    b1 = 0.000073637 + 0.00000017945 * T
    b0 = -0.01922 - 0.0000442 * T
    B4 = b0 + b1 * p
    #' S**1 term
    a3 = (-3.389E-13 * T + 0.000000000006649) * T + 0.00000000011
    A2 = ((0.000000000007988 * T - 0.00000000016002) * T + 0.0000000091041) * T - 0.00000039064
    A1 = (((-0.00000000020122 * T + 0.000000010507) * T - 0.000000064885) * T - 0.00001258) * T + 0.000094742
    A0 = (((-0.0000000321 * T + 0.000002006) * T + 0.00007164) * T - 0.01262) * T + 1.389
    A4 = ((a3 * p + A2) * p + A1) * p + A0
    #' s**0 term
    c3 = (-2.3643E-12 * T + 0.00000000038504) * T - 0.0000000097729
    C2 = (((1.0405E-12 * T - 0.00000000025335) * T + 0.000000025974) * T - 0.0000017107) * T + 0.00003126
    C1 = (((-0.00000000061185 * T + 0.00000013621) * T - 0.0000081788) * T + 0.00068982) * T + 0.153563
    C0 = ((((0.0000000031464 * T - 0.000001478) * T + 0.0003342) * T - 0.0580852) * T + 5.03711) * T + 1402.388
    C4 = ((c3 * p + C2) * p + C1) * p + C0
    
    #' sound speed return
    return C4 + (A4 + B4 * sr + D * S) * S    
    
def MacKenzie(T, S, D):
  '''from: http://resource.npl.co.uk/acoustics/techguides/soundseawater/content.html
     T = temperature in degrees Celsius
     S = salinity in parts per thousand
     D = depth in metres
  '''

  if T < 2. or T > 30.:
    raise ValueError("MacKenzie equation is only valid with temperature ranging: 2 < T < 30 degrees celcius (%.02f given)" % T)

  if S < 25. or S > 40.:
    raise ValueError("MacKenzie equation is only valid with salinity ranging: 25 < S < 40 PSU (parts per thousand) (%.02f given)" % S)

  if D < 0. or D > 8000.:
    raise ValueError("MacKenzie equation is only valid with depth ranging: 0 < S < 8000 meters (%.02f given)" % P)

  return 1448.96 + 4.591 * T - 5.304E-2 * T * T + 2.374E-4 * pow(T, 3) + \
         1.340 (S - 35.) + 1.630E-2 * D + 1.675E-7 * D * D - 1.025E-2 * T * (S - 35.) - \
         7.139E-13 * T * pow(D, 3)

def Coppens(T, S, D):
  '''from: http://resource.npl.co.uk/acoustics/techguides/soundseawater/content.html
     T = temperature in degrees Celsius
     S = salinity in parts per thousand
     D = depth in meters
  '''
  if T < 0. or T > 35.:
    raise ValueError("Coppens equation is only valid with temperature ranging: 0 < T < 35 degrees celcius (%.02f given)" % T)

  if S < 0. or S > 45.:
    raise ValueError("Coppens equation is only valid with salinity ranging: 0 < S < 45 PSU (parts per thousand) (%.02f given)" % S)

  if D < 0. or D > 4000.:
    raise ValueError("Coppens equation is only valid with depth ranging: 0 < S < 4000 meters (%.02f given)" % P)

  T /= 10.
  D /= 1000.

  return Cop0(S,T) + (16.23 + 0.253 * T) * D + \
         (0.213-0.1 * T) * D * D + ( 0.016 + 0.0002 * (S-35.) ) * (S - 35.) * T * D

def Cop0(S, T):
  return 1449.05 + 45.7 * T - 5.21 * T * T + 0.23 * pow(T, 3) + (1.333 - 0.126 * T + 0.009 * T * T) * (S - 35.)
  

'''Wilson's formula looks as follows:
http://www.akin.ru/spravka_eng/s_i_svel_e.htm

c(S,T,P) = c0 + D cT + D cS + D cP + D cSTP, 
c0 = 1449.14, 
D cT = 4.5721T - 4.4532e-2 T^2 - 2.6045e-4 T^3 + 7.9851e-6 T^4,  
D cS = 1.39799(S-35) - 1.69202e-3 (S-35)^2,  
D cP = 1.63432 P - 1.06768e-3 P^2 + 3.73403e-6 P^3 - 3.6332e-8 P^4,  
D cSTP = (S-35)(-1.1244e-2 T + 7.7711e-7 T^2 + 7.85344e-4 P -  
               - 1.3458e-5 P^2 + 3.2203e-7 P*T + 1.6101e-8 T^2 * P) +  
               + P(-1.8974e-3 T + 7.6287e-5 T^2 + 4.6176e-7 T^3) +  
               + P^2(-2.6301e-5 T + 1.9302e-7 T^2) + P^3(-2.0831e-7 T),  

where c(S,T,P) - speed of sound, m/s; T - temperature, degC; S - salinity, per mille; P - hydrostatic pressure, MPa. 

Wilson's formula is valid for the following ranges of temperature, salinity, and hydrostatic pressure: 

temperature from -4deg to 30deg; 
salinity from 0 to 37 per mille; 
hydrostatic pressure from 0.1 MPa to 100 MPa. 
The mean-square error of calculation of the speed of sound via this formula with regard to Wilson's experimental data is 0.22 m/s. 
'''

'''
>>> Wilson(0, 35, .1)
1449.3
'''
def Wilson_SeaBird(S, T, p):
    '''
    ' Sea-Bird's version of Wilson's Equation using Double Precision variables.
    
    ' /* wilson JASA, 1960, 32, 1357 */
    ' // s = salinity, t = temperature deg C ITPS-68, p = pressure in decibars
    
    ' RLB 3/31/2008 This function was taken from Derived Parameters Formulas in
    ' Sea-Bird manual SBEDataProcessing_7.16a.pdf.
    ' Code was modified for Visual Basic 6 from C.
    '''
    pr = 0.1019716 * (p + 10.1325)
    Sd = S - 35#
    A = (((0.0000079851 * T - 0.00026045) * T - 0.044532) * T + 4.5721) * T + 1449.14
    SV = (0.00000077711 * T - 0.011244) * T + 1.39799
    v0 = (0.00169202 * Sd + SV) * Sd + A
    A = ((0.000000045283 * T + 0.0000074812) * T - 0.00018607) * T + 0.16072
    SV = (0.000000001579 * T + 0.00000003158) * T + 0.000077016
    V1 = SV * Sd + A
    A = (0.0000000018563 * T - 0.00000025294) * T + 0.000010268
    SV = -0.00000012943 * Sd + A
    A = -0.00000000019646 * T + 0.0000000035216
    SV = (((-3.3603e-12 * pr + A) * pr + SV) * pr + V1) * pr + v0
    return SV


DG_Coefficients = '''
C000 1402.392 
CT1 0.5012285E1 
CT2 -0.551184E-1 
CT3 0.221649E-3 
CS1 0.1329530E1 
CS2 0.1288598E-3 
CP1 0.1560592 
CP2 0.2449993E-4 
CP3 -0.8833959E-8 
CST -0.1275936E-1 
CTP 0.6353509E-2 
CT2P2 0.2656174E-7 
CTP2 -0.1593895E-5 
CTP3 0.5222483E-9 
CT3P -0.4383615E-6 
CS2P2 -0.1616745E-8 
CST2 0.9688441E-4 
CS2TP 0.4857614E-5 
CSTP -0.3406824E-3 
'''
DG_doc=''' Del Grosso
  c(S,T,P) =   C000 + CT + CS + CP + CSTP    
  
  CT(T) = CT1T + CT2T2 + CT3T3  
  CS(S) = CS1S + CS2S2  
  CP(P) = CP1P + CP2P2 + CP3P3  
  CSTP(S,T,P) = CTPTP + CT3PT3P + CTP2TP2 + CT2P2T2P2 + CTP3TP3 + CSTST + CST2ST2 + CSTPSTP + CS2TPS2TP + CS2P2S2P2  
  
T = temperature in degrees Celsius
S = salinity in Practical Salinity Units
P = pressure in kg/cm2  

Range of validity: temperature 0 to 30 degC, salinity 30 to 40 parts per thousand, pressure 0 to 1000 kg/cm2, where 100 kPa=1.019716 kg/cm2
'''
dgall = coefficients.split()
while True:
  try:
    val, var = dgall.pop(), dgall.pop()
  except IndexError: break
  s =  "%s = %s" % (var, val)
  exec(s)


def DelGrosso(S, T, P):
    '''DelGrosso formula for sound speed from salinity, temperature, pressue.
    T = temperature in degrees Celsius
    S = salinity in Practical Salinity Units
    P = pressure in kg/cm2
    '''  
    return C000 + CT + CS + CP + CSTP    

def CSTP(S,T,P):
    P2=numpy.power(P,2)
    T2=numpy.power(T,2)
    S2=numpy.power(S,2)
    return CTP*T*P + CTP2*T*P2 + CT2P2*T2*P2 + CT3P*T**3*P + CTP3*T*P**3 + \
           CST*S*T + CST2*S*T2 + CS2P2*S2*P2 + CSTP*S*T*P + CS2TP*S2*T*P  

def CT(T):
    return CT1*T + CT2*T**2 + CT3**T3  
def CS(S):
    return CS1*S + CS2*S**2
def CP(P):
    return CP1*P + CP2*P**2 + CP3*P**3  


''' Pressure to Depth
  ZS(P,L) =   (9.72659 x 10^2P - 2.2512 x 10^-1 P^2 + 2.279 x 10^-4 P^3 - 1.82 x 10^-7 P^4)/ 
                (  g(L) + 1.092 x 10^-4 P )  

  Where g(L), the international formula for gravity, is given by:

  g(L) =   9.780318 (1 + 5.2788 x 10^-3 sin(L)^2 + 2.36 x 10^-5 sin(L)^4 )
    
  Z = depth in metres
  P = pressure in MPa (relative to atmospheric pressure)
  L = latitude 
  
The above equation is true for the oceanographers' standard ocean, defined as an ideal medium with a temperature of 0 degC and salinity of 35 parts per thousand.

Leroy and Parthiot (1998) give a table of corrections which are needed when the standard formula is applied to specific oceans and seas. The above equation and interactive version do not apply any corrections.
http://lib.ioa.ac.cn/ScienceDB/JASA/jasa1998/pdfs/vol_103/iss_3/1346_1.pdf
  
'''

def DensityFromTSP(T, S, p0):
    '''
    ' This function is adapted from NODC FORTRAN code.
    '     FDENSE CALCULATES DENSITY
    '      T - TEMPERATURE DEG CELSIUS
    '      S - SALINITY PSU
    '      P - PRESSURE DECIBARS (CHANGED TO BARS FOR CALCULATIONS)
    
    ' Real KW, KSTO, KSTP
    ' Use the 1980 equation of state (EOS-80) in UNESCO 1983 paper
    '''
    p = p0 * 0.1

    T2 = numpy.power(T,2)
    T3 = numpy.power(T,3)
    T4 = numpy.power(T,4)
    p2 = numpy.power(p,2)
    S1_5 = S**1.5
    
    RW = 999.842594 + 0.06793952 * T - 0.00909529 * T2 + \
            0.0001001685 * T3 - 0.000001120083 * T4 + 0.000000006536332 * T**5
    
    RSTO = RW + (0.824493 - 0.0040899 * T + 0.000076438 * T2 \
           - 0.00000082467 * T3 + 0.0000000053875 * T4) * S \
           + (-0.00572466 + 0.00010227 * T - 0.0000016546 * T2) * S1_5 \
           + 0.00048314 * S**2
    
    KW = 19652.21 + 148.4206 * T - 2.327105 * T2 + 0.01360477 * T3 \
            - 0.00005155288 * T4
    
    KSTO = KW + (54.6746 - 0.603459 * T + 0.0109987 * T2 \
            - 0.00006167 * T3) * S \
           + (0.07944 + 0.016483 * T - 0.00053009 * T2) * S1_5
    
    KSTP = KSTO + (3.239908 + 0.00143713 * T + 0.000116092 * T2 \
            - 0.000000577905 * T3) * p \
           + (0.0022838 - 0.000010981 * T - 0.0000016078 * T2) * p * S \
           + 0.000191075 * p * S1_5 \
           + (0.0000850935 - 0.00000612293 * T + 0.000000052787 * T2) * p2 \
           + (-0.00000099348 + 0.000000020816 * T + 0.00000000091697 * T2) * p2 * S
    
    return RSTO / (1.0 - p / KSTP) - 1000.0



def Extend_Slope(prof, p, inner=False):
    '''
    Copied this function from ExtendSlope Profile.py
    
    ' Compute the most probable slope for a given cast and use it
    ' to extend the cast down
    
    ' PROGRAMMER: Dr. Lloyd Huff                     DATE: 2/25/88
    
    ' Modified 9/2008 to avoid division by zero.
    '''

    X = prof['pressure']
    Y = prof['salinity'] if inner else prof['temperature']
    #' RLB 9/2008 Adjustment for case of AUV processing, for which there
    #' is a possibility of duplicate max depth points.
    dx = numpy.hstack(([1],numpy.diff(X)))
    X = X.compress(dx>0)
    Y = Y.compress(dx>0)
    XM = X*0.0
    HBC = numpy.zeros([11], numpy.float32)
    CBC = numpy.zeros([11], numpy.float32)
    H = numpy.zeros([11], numpy.float32)
    
    G = len(X) - 2                     # ' Index for next to last point is G
    
    Xmid = 0.5 * (X[G] + X[G + 1]) #' Extrapolation will start from point
    Ymid = 0.5 * (Y[G] + Y[G + 1]) #' halfway between deepest 2 points
    
    NumSlopes = G+1
    for K in range(NumSlopes):
        Dx = X[K] - X[G + 1]
        Dy = Y[K] - Y[G + 1]
        #' Compute slope between last point and all others.
        XM[K] = Dy / Dx
    XMmin = XM[:NumSlopes].min() #' Find the range of slopes
    XMmax = XM[:NumSlopes].max()
    
    Hnum = 10 if NumSlopes > 10 else NumSlopes - 1 #  ' Set # of histogram bins
    HBW = (XMmax - XMmin) / Hnum          #       ' Set width of bins
    for K in range(Hnum):
        HBC[K] = XMmin + (K - 0.5) * HBW    #      ' Set centers of bins
    
    for J in range(NumSlopes):#                    ' Populate histogram
        for I in range(Hnum):#                      ' Weight by depth spacing
            if XM[J] >= HBC[I] - 0.75 * HBW and XM[J] <= HBC[I] + 0.75 * HBW :
                H[I] = H[I] + X[J + 1] - X[J]

    Hmax = 0
    for I in range(Hnum): #             'Find largest number of entries in bins
        if H[I] >= Hmax: Hmax = H[I]
        if H[I] == Hmax: Slope = HBC[I]
    
    #' Determine if more than one bin has largest number of entries
    Count = 0
    for I in range(Hnum):
        if H[I] == Hmax: Count = Count + 1

    if Count <> 1:
        #' Find which of several bins with largest number of entries
        #' has a slope closest to that between last two points in data set.
        for J in range(Hnum):
            CBC[J] = 500
            if H[J] == Hmax: CBC[J] = numpy.absolute(XM[NumSlopes] - XM[J])

        Ref = 500
        for J in range(Hnum):
            if CBC[J] < Ref: Ref = CBC[J]
            if CBC[J] == Ref: Slope = HBC[J]

    if inner: return np.append(Y, Ymid + (p - Xmid) * Slope)        
    rtn = {}
    rtn['pressure'] = np.append(X, p)
    rtn['temperature'] = np.append(Y, Ymid + (p - Xmid) * Slope)
    rtn['salinity'] = Extend_Slope(prof, p, inner=True)
    return rtn


def PressureToDepth(p, LAT):
    '''
    ' originally named FDEPTH from NODC.
    ' This function is adapted from NODC FORTRAN code.
    '*********************************************************************
    ' Depth in meters from pressure in decibars using Saunders
    ' and Fofonoff's method.
    ' Deep-Sea Res., 1976,23,109-111.
    ' Formula refitted for 1980 equation of state units:
    '          Pressure        P         Decibars
    '          Latitude        LAT       Degrees
    '          Depth           DEPTH     Meters
    ' Checkvalue:  DEPTH=9712.653 M for P=10000 Decibars, LATITUDE=30 Degrees
    ' Above for station ocean: T=0 Degree Celsius; S=35 (PSS-78)
    '*********************************************************************
    '''   
    X = numpy.sin(LAT * sbe_constants.DEG2RAD())**2
    #'* GR=Gravity variation with Latitude: ANON (1970) Bulletin Geodesique
    GR = 9.780318 * (1.0 + (5.2788e-3 + 2.36e-5 * X) * X) + 1.092e-6 * p
    rval = (((-1.82e-15 * p + 2.279e-10) * p - 2.2512e-5) * p + 9.72659) * p
    return rval / GR
 
  
''' depth into pressure
P(Z,L) =  h(Z,L) - Lxh0xZ 
    
h(Z,L) =  h(Z,45) x k(Z,L) 
  
h(Z,45) =   1.00818 x 10^-2 Z + 2.465 x 10^-8 Z^2 - 1.25 x 10^-13 Z^3 + 2.8 x 10^-19 Z^4  
  
k(Z,L) =   (g(L) - 2 x 10^-5 Z)/(9.80612 - 2 x 10^-5 Z)  
  
g(L) =   9.7803(1 + 5.3 x 10^-3 sin(L)^2)  
    
h0Z = 1.0x10^-2 Z/(Z+100) + 6.2x10^-6 Z 
  
Z = depth in metres
h = pressure in MPa (relative to atmospheric pressure)
L = latitude
 
In the above equation, P (=h(Z,L)) would apply to the oceanographers' standard ocean, defined as an ideal medium with a temperature of 0 degC and salinity of 35 parts per thousand.

Leroy and Parthiot (1998) give a table of corrections which are needed when the standard formula is applied to specific oceans and seas. The correction h0Z is the correction applicable to common oceans. These are defined as open oceans between the latitudes of 60degN and 40degS, and excluding closed ocean basins and seas. A full range of corrections may be found in Leroy and Parthiot (1998).
 
http://lib.ioa.ac.cn/ScienceDB/JASA/jasa1998/pdfs/vol_103/iss_3/1346_1.pdf

'''


def gsw_Hill_ratio_at_SP2(t):
    '''
    % gsw_Hill_ratio_at_SP2                               Hill ratio at SP of 2
    %==========================================================================
    %
    % USAGE:  
    %  Hill_ratio = gsw_Hill_ratio_at_SP2(t)
    %
    % DESCRIPTION:
    %  Calculates the Hill ratio, which is the adjustment needed to apply for
    %  Practical Salinities smaller than 2.  This ratio is defined at a 
    %  Practical Salinity = 2 and in-situ temperature, t using PSS-78. The Hill
    %  ratio is the ratio of 2 to the output of the Hill et al. (1986) formula
    %  for Practical Salinity at the conductivity ratio, Rt, at which Practical
    %  Salinity on the PSS-78 scale is exactly 2.
    %
    % INPUT:
    %  t  =  in-situ temperature (ITS-90)                             [ deg C ]
    %
    % OUTPUT:
    %  Hill_ratio  =  Hill ratio at SP of 2                        [ unitless ]
    %
    % AUTHOR:  
    %  Trevor McDougall and Paul Barker                    [ help@teos-10.org ]
    %
    % VERSION NUMBER: 3.04 (10th December, 2013)
    %
    % REFERENCES:
    %  Hill, K.D., T.M. Dauphinee & D.J. Woods, 1986: The extension of the 
    %   Practical Salinity Scale 1978 to low salinities. IEEE J. Oceanic Eng.,
    %   11, 109 - 112.
    %
    %  IOC, SCOR and IAPSO, 2010: The international thermodynamic equation of 
    %   seawater - 2010: Calculation and use of thermodynamic properties.  
    %   Intergovernmental Oceanographic Commission, Manuals and Guides No. 56,
    %   UNESCO (English), 196 pp.  Available from http://www.TEOS-10.org
    %    See appendix E of this TEOS-10 Manual.  
    %
    %  McDougall, T.J. and S.J. Wotherspoon, 2012: A simple modification of 
    %   Newton's method to achieve convergence of order "1 + sqrt(2)".
    %   Submitted to Applied Mathematics and Computation.  
    %
    %  Unesco, 1983: Algorithms for computation of fundamental properties of 
    %   seawater. Unesco Technical Papers in Marine Science, 44, 53 pp.
    %
    %  The software is available from http://www.TEOS-10.org
    %
    %==========================================================================
    '''
    
    SP2 = 2*(numpy.ones(t.shape))
    
    #%--------------------------------------------------------------------------
    #% Start of the calculation
    #%--------------------------------------------------------------------------
    
    a0 =  0.0080
    a1 = -0.1692
    a2 = 25.3851
    a3 = 14.0941
    a4 = -7.0261
    a5 =  2.7081
    
    b0 =  0.0005
    b1 = -0.0056
    b2 = -0.0066
    b3 = -0.0375
    b4 =  0.0636
    b5 = -0.0144
    
    g0 = 2.641463563366498e-1
    g1 = 2.007883247811176e-4
    g2 = -4.107694432853053e-6
    g3 = 8.401670882091225e-8
    g4 = -1.711392021989210e-9
    g5 = 3.374193893377380e-11
    g6 = -5.923731174730784e-13
    g7 = 8.057771569962299e-15
    g8 = -7.054313817447962e-17
    g9 = 2.859992717347235e-19
    
    k  =  0.0162
    
    t68 = t*1.00024
    ft68 = (t68 - 15)/(1 + k*(t68 - 15))
    
    #%--------------------------------------------------------------------------
    #% Find the initial estimates of Rtx (Rtx0) and of the derivative dSP_dRtx
    #% at SP = 2. 
    #%--------------------------------------------------------------------------
    Rtx0 = g0 + t68*(g1 + t68*(g2 + t68*(g3 + t68*(g4 + t68*(g5 + t68*(g6 + t68*(g7 + t68*(g8 + t68*g9))))))))
         
    dSP_dRtx =  a1 + (2*a2 + (3*a3 + (4*a4 + 5*a5*Rtx0)*Rtx0)*Rtx0)*Rtx0 + ft68*(b1 + (2*b2 + (3*b3 + (4*b4 + 5*b5*Rtx0)*Rtx0)*Rtx0)*Rtx0)    
    
    #%--------------------------------------------------------------------------
    #% Begin a single modified Newton-Raphson iteration (McDougall and 
    #% Wotherspoon, 2012) to find Rt at SP = 2.
    #%--------------------------------------------------------------------------
    SP_est = a0 + (a1 + (a2 + (a3 + (a4 + a5*Rtx0)*Rtx0)*Rtx0)*Rtx0)*Rtx0 + ft68*(b0 + (b1 + (b2+ (b3 + (b4 + b5*Rtx0)*Rtx0)*Rtx0)*Rtx0)*Rtx0)
    Rtx = Rtx0 - (SP_est - SP2)/dSP_dRtx
    Rtxm = 0.5*(Rtx + Rtx0)
    dSP_dRtx =  a1 + (2*a2 + (3*a3 + (4*a4 + 5*a5*Rtxm)*Rtxm)*Rtxm)*Rtxm + ft68*(b1 + (2*b2 + (3*b3 + (4*b4 + 5*b5*Rtxm)*Rtxm)*Rtxm)*Rtxm)
    Rtx = Rtx0 - (SP_est - SP2)/dSP_dRtx
    
    #% This is the end of one full iteration of the modified Newton-Raphson 
    #% iterative equation solver.  The error in Rtx at this point is equivalent 
    #% to an error in SP of 9e-16 psu.  
                                    
    x = 400*Rtx*Rtx
    sqrty = 10*Rtx
    part1 = 1 + x*(1.5 + x)
    part2 = 1 + sqrty*(1 + sqrty*(1 + sqrty))
    SP_Hill_raw_at_SP2 = SP2 - a0/part1 - b0*ft68/part2
    
    return 2.0/SP_Hill_raw_at_SP2
    
#print c,t,p
#(array([ 4.445,  4.53 ]), array([ 17.628,  17.805]), array([ 1.125,  5.031]))    
#s=SVEquations.SalinityFromConductivity(c, t, p)
#print s
#array([ 34.07479104,  34.65257945])
#print SVEquations.ChenMillero(t, s, p)
#array([ 1513.66328866,  1514.90793605])
def SalinityFromConductivity(c, t, p):
    '''pass in conductivity in mS/cm, Temp in C, and pressure in dbar and get back Practical Salinity (unitless)
    function SP = gsw_SP_from_C(C,t,p)
    
    % gsw_SP_from_C                        Practical Salinity from conductivity 
    %==========================================================================
    %
    % USAGE: 
    %  SP = gsw_SP_from_C(C,t,p)
    %
    % DESCRIPTION:
    %  Calculates Practical Salinity, SP, from conductivity, C, primarily using
    %  the PSS-78 algorithm.  Note that the PSS-78 algorithm for Practical 
    %  Salinity is only valid in the range 2 < SP < 42.  If the PSS-78 
    %  algorithm produces a Practical Salinity that is less than 2 then the 
    %  Practical Salinity is recalculated with a modified form of the Hill et 
    %  al. (1986) formula.  The modification of the Hill et al. (1986)
    %  expression is to ensure that it is exactly consistent with PSS-78 
    %  at SP = 2.  Note that the input values of conductivity need to be in 
    %  units of mS/cm (not S/m). 
    %
    % INPUT:
    %  C  =  conductivity                                             [ S/m ]
    %  t  =  in-situ temperature (ITS-90)                             [ deg C ]
    %  p  =  sea pressure                                              [ dbar ]
    %        ( i.e. absolute pressure - 10.1325 dbar )
    %
    %  t & p may have dimensions 1x1 or Mx1 or 1xN or MxN, where C is MxN.
    %
    % OUTPUT:
    %  SP  =  Practical Salinity on the PSS-78 scale               [ unitless ]
    %
    % AUTHOR:  
    %  Paul Barker, Trevor McDougall and Rich Pawlowicz    [ help@teos-10.org ]
    %
    % VERSION NUMBER: 3.04 (10th December, 2013)
    %
    % REFERENCES:
    %  Culkin and Smith, 1980:  Determination of the Concentration of Potassium  
    %   Chloride Solution Having the Same Electrical Conductivity, at 15C and 
    %   Infinite Frequency, as Standard Seawater of Salinity 35.0000 
    %   (Chlorinity 19.37394), IEEE J. Oceanic Eng, 5, 22-23.
    %
    %  Hill, K.D., T.M. Dauphinee & D.J. Woods, 1986: The extension of the 
    %   Practical Salinity Scale 1978 to low salinities. IEEE J. Oceanic Eng.,
    %   11, 109 - 112.
    %
    %  IOC, SCOR and IAPSO, 2010: The international thermodynamic equation of 
    %   seawater - 2010: Calculation and use of thermodynamic properties.  
    %   Intergovernmental Oceanographic Commission, Manuals and Guides No. 56,
    %   UNESCO (English), 196 pp.  Available from http://www.TEOS-10.org
    %    See appendix E of this TEOS-10 Manual. 
    %
    %  Unesco, 1983: Algorithms for computation of fundamental properties of 
    %   seawater. Unesco Technical Papers in Marine Science, 44, 53 pp.
    %
    %  The software is available from http://www.TEOS-10.org
    %
    %==========================================================================
    
    '''

    
#    mc,nc = C.shape
#    mt,nt = t.shape
#    mp,np = p.shape
#    
#    if (mt == 1) and (nt == 1):        #      % t scalar - fill to size of C
#        t = t*numpy.ones(C.shape)
#    elif (nc == nt) and (mt == 1):   #      % t is row vector,
#        t = t(ones(1,mc), :)          #    % copy down each column.
#    elif (mc == mt) & (nt == 1):      #   % t is column vector,
#        t = t(:,ones(1,nc));           #    % copy across each row.
#    elif (nc == mt) & (nt == 1):      #    % t is a transposed row vector,
#        t = t.transpose()              #                 % transposed then
#        t = t(ones(1,mc), :)           #         % copy down each column.
#    elif (mc == mt) & (nc == nt):
#        % ok
#    else:
#        raise Exception('gsw_SP_from_C: Inputs array dimensions arguments do not agree')
#
#    
#    if (mp == 1) & (np == 1)              % p scalar - fill to size of C
#        p = p*ones(size(C));
#    elseif (nc == np) & (mp == 1)         % p is row vector,
#        p = p(ones(1,mc), :);              % copy down each column.
#    elseif (mc == mp) & (np == 1)         % p is column vector,
#        p = p(:,ones(1,nc));               % copy across each row.
#    elseif (nc == mp) & (np == 1)          % p is a transposed row vector,
#        p = p.';                                         % transposed then
#        p = p(ones(1,mc), :);                    % copy down each column.
#    elseif (mc == mp) & (nc == np)
#        % ok
#    else
#        error('gsw_SP_from_C: Inputs array dimensions arguments do not agree')
#    end %if
#    
#    if mc == 1
#        C = C.';
#        t = t.';
#        p = p.';
#        transposed = 1;
#    else
#        transposed = 0;
#    end
    
    #%--------------------------------------------------------------------------
    #% Start of the calculation
    #%--------------------------------------------------------------------------
    
    #switch conductivity from S/m to ms/cm
    C = c*10.0
    
    a0 =  0.0080
    a1 = -0.1692
    a2 = 25.3851
    a3 = 14.0941
    a4 = -7.0261
    a5 =  2.7081
    
    b0 =  0.0005
    b1 = -0.0056
    b2 = -0.0066
    b3 = -0.0375
    b4 =  0.0636
    b5 = -0.0144
    
    c0 =  0.6766097
    c1 =  2.00564e-2
    c2 =  1.104259e-4
    c3 = -6.9698e-7
    c4 =  1.0031e-9
    
    d1 =  3.426e-2
    d2 =  4.464e-4
    d3 =  4.215e-1
    d4 = -3.107e-3
    
    e1 =  2.070e-5
    e2 = -6.370e-10
    e3 =  3.989e-15
    
    k  =  0.0162
    
    # Iocean was used to remove any measurements that aren't realistic --  not in water etc.
    # for now, we'll assume all measurements are good.
    # To add this functionality do a compress on C, t, p based on whatever criteria we'd want 
    #[Iocean] = numpy.arange( find(~isnan(C + t + p))
    
    t68 = t*1.00024;
    ft68 = (t68 - 15)/(1 + k*(t68 - 15))
    
    #% The dimensionless conductivity ratio, R, is the conductivity input, C,
    #% divided by the present estimate of C(SP=35, t_68=15, p=0) which is 
    #% 42.9140 mS/cm (=4.29140 S/m), (Culkin and Smith, 1980). 
    
    R = 0.023302418791070513*C          #%   0.023302418791070513 = 1./42.9140
    
    #% rt_lc corresponds to rt as defined in the UNESCO 44 (1983) routines.  
    rt_lc = c0 + (c1 + (c2 + (c3 + c4*t68)*t68)*t68)*t68
    Rp = 1 + (p*(e1 + e2*p + e3*p*p)) / (1 + d1*t68 + d2*t68*t68 + (d3 + d4*t68)*R)
    Rt = R/(Rp*rt_lc)  
    
    Rt[numpy.where(Rt < 0)] = numpy.nan
    
    Rtx = numpy.sqrt(Rt)
    
    #SP = NaN(C.shape);
    
    SP = a0 + (a1 + (a2 + (a3 + (a4 + a5*Rtx)*Rtx)*Rtx)*Rtx)*Rtx + ft68*(b0 + (b1 + (b2 + (b3 + (b4 + b5*Rtx)*Rtx)*Rtx)*Rtx)*Rtx)
    
    #% The following section of the code is designed for SP < 2 based on the
    #% Hill et al. (1986) algorithm.  This algorithm is adjusted so that it is
    #% exactly equal to the PSS-78 algorithm at SP = 2.
    
    if numpy.any(SP < 2):
        #[I2] = find(SP(Iocean) < 2);
        #make a copy of the temps and pass them to the Hill ratio 
        Hill_ratio = gsw_Hill_ratio_at_SP2(t[:]) 
        x = 400*Rt;
        sqrty = 10*Rtx;
        part1 = 1 + x*(1.5 + x)
        part2 = 1 + sqrty*(1 + sqrty*(1 + sqrty))
        SP_Hill_raw = SP - a0/part1 - b0*ft68/part2
        SP = numpy.where(SP<2, Hill_ratio*SP_Hill_raw, SP)
    
    #% This line ensures that SP is non-negative.
    SP=numpy.maximum(SP, 0)
    
    return SP