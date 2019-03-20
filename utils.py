import time,datetime
def getUnixTime():
    return int(time.time())

def UnixToDatetime(utime):
    return datetime.datetime.fromtimestamp(utime)

def DatetimeToUnix(dtime):
    return int(time.mktime(dtime.timetuple()))

