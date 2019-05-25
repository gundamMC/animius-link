import datetime
import http.client
import time


def getUnixTime():
    return int(time.time())


def UnixToDatetime(utime):
    return datetime.datetime.fromtimestamp(utime)


def DatetimeToUnix(dtime):
    return int(time.mktime(dtime.timetuple()))


def amlink_exit(id):
    return {'id': id, 'status': '', 'message': 'success', 'data': {}}


def amlink_check_update(id):
    return {'id': id, 'status': '', 'message': 'success', 'data': {}}


def amlink_check_internet(id):
    conn = http.client.HTTPConnection("www.cloudflare.com", timeout=5)
    try:
        conn.request("HEAD", "/")
        conn.close()
        return {'id': id, 'status': '', 'message': 'success', 'data': {}}
    except:
        conn.close()
        return {'id': id, 'status': '', 'message': 'timeout', 'data': {}}
