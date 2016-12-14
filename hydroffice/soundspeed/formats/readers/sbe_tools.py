import time
import datetime

def DayOfYear(Mon, Day, Yr):
    ''' Calculate the day-of-year corresponding to a given month, day, year
        Version 8.84: Modified code to correct calculation for leap year for case of
        a year which is an end-of-century year.
              
        Note: At this time, the input variable Yr may be a 1-digit, 2-digit or 4-digit integer.
              Ex: 0, 1, 98, 1999, 2006
    '''
    Mon, Day, Yr = int(Mon), int(Day), int(Yr)
    if Yr<80: Yr+=2000
    if Yr<100: Yr+=1900
    d=datetime.datetime(Yr, Mon, Day)
    return d.toordinal() - datetime.date(d.year, 1, 1).toordinal() + 1 #same as d.timetuple()[7] but slightly quicker

def MonthDay(year, doy):
    d = datetime.date.fromordinal(datetime.date(int(year),1,1).toordinal()+int(doy)-1)
    return d.month, d.day