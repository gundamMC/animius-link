import datetime
import http.client
import time


def getUnixTime():
    return int(time.time())


def UnixToDatetime(utime):
    return datetime.datetime.fromtimestamp(utime)


def DatetimeToUnix(dtime):
    return int(time.mktime(dtime.timetuple()))


def amlink_exit():
    return '', 'success', {}


def amlink_check_update():
    return '', 'success', {}


def amlink_check_internet():
    conn = http.client.HTTPConnection("www.cloudflare.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return '', 'success', {}
    except:
        conn.close()
        return '', 'timeout', {}
