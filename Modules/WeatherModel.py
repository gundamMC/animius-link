import requests
from xml.etree import ElementTree as ET


def nodetextToDict(node):
    """
    :param node: ET.Element
    :return: a dict in form of {tag:({"item1":"".....},[{child}..../text])}
    """
    if len(list(node)) == 0:
        return node.text
    d = dict()
    for cNode in list(node):
        if cNode.tag in d.keys():
            d[cNode.tag].append((dict(cNode.items()), nodetextToDict(cNode)))
        else:
            d[cNode.tag] = [(dict(cNode.items()), nodetextToDict(cNode))]
    return d


# TODO: unit conversion

class _ComWeatherCurrent(object):
    def __init__(self):
        self._latestUpdateTime = ""
        self._location = ""
        self._tmp = "0"  # F
        self._tmp_FeelLike = "0"  # F
        self._weather_desc = ""
        self._uv_index = "0"  # out of 10
        self._uv_desc = ""
        self._humidity = "0"  # percent
        self._visibility = "0"  # meter
        self._wind_direction_text = ""
        self._wind_direction = "0"
        self._wind_speed = "0"  # mph
        self._pressure = "0"  # in
        self._dew_point = "0"  # F

        self._unit_speed = "mph"
        self._unit_distance = "mile"
        self._unit_tmp = "F"
        self._unit_pressure = "in"

    @classmethod
    def initFromXML(cls, node):
        w = cls()
        node = nodetextToDict(node)
        w._latestUpdateTime = node["lsup"][0][1]
        w._location = node["obst"][0][1]
        w._tmp = node["tmp"][0][1]
        w._tmp_FeelLike = node["flik"][0][1]
        w._weather_desc = node["t"][0][1]
        w._dew_point = node["dewp"][0][1]
        w._humidity = node["hmid"][0][1]
        w._visibility = node["vis"][0][1]
        w._pressure = node["bar"][0][1]["r"][0][1]
        w._wind_speed = node["wind"][0][1]["s"][0][1]
        w._wind_direction_text = node["wind"][0][1]["t"][0][1]
        w._wind_direction = node["wind"][0][1]["d"][0][1]
        w._uv_desc = node["uv"][0][1]["t"][0][1]
        w._uv_index = node["uv"][0][1]["i"][0][1]
        return w

    @property
    def wind(self):
        return "%s %s %s " % (self._wind_direction_text, self._wind_speed, self._unit_speed)

    @property
    def humidity(self):
        return "%s%%" % (self._humidity)

    @property
    def temperature(self):
        return "%s %s" % (self._tmp, self._unit_tmp)

    @property
    def temperatureFL(self):
        return self._tmp_FeelLike + self._unit_tmp

    @property
    def uv(self):
        return "%s/10 (%s)" % (self._uv_index, self._uv_desc)

    @property
    def pressure(self):
        return "%s %s" % (self._pressure, self._unit_pressure)

    @property
    def visibility(self):
        return "%s %s" % (self._visibility, self._unit_distance)

    @property
    def dew_point(self):
        return "%s %s" % (self._dew_point, self._unit_tmp)

    @property
    def location(self):
        return self._location

    @property
    def latestUpdateTime(self):
        return self._latestUpdateTime

    @property
    def weather(self):
        return self._weather_desc


class _ComWeatherDay(object):
    def __init__(self):
        self._latestUpdateTime = ""
        self._date = ""
        self._day = ""
        self._tmp_highest = "0"
        self._tmp_lowest = "0"
        self._sunrise = ""
        self._sunset = ""

        self._day_weather_desc = ""
        self._day_wind_speed = "0"
        self._day_wind_direction = "0"
        self._day_wind_direction_text = ""
        self._day_humidity = "0"
        self._day_precipitation_chance = "0"

        self._night_weather_desc = ""
        self._night_wind_speed = "0"
        self._night_wind_direction_text = ""
        self._night_wind_direction = "0"
        self._night_humidity = "0"
        self._night_precipitation_chance = "0"

        self._unit_speed = "mph"
        self._unit_distance = "mile"
        self._unit_tmp = "F"
        self._unit_pressure = "in"

    @classmethod
    def initFromXML(cls, node):
        node = nodetextToDict(node)
        weathers = []
        for day in node["day"]:
            w = cls()
            w._latestUpdateTime = node["lsup"][0][1]
            w._date = day[0]["dt"]
            w._day = day[0]["t"]
            w._tmp_highest = day[1]["hi"][0][1]
            w._tmp_lowest = day[1]["low"][0][1]
            w._sunrise = day[1]["sunr"][0][1]
            w._sunset = day[1]["suns"][0][1]

            w._day_weather_desc = day[1]["part"][0][1]["t"][0][1]
            w._day_wind_speed = day[1]["part"][0][1]["wind"][0][1]["s"][0][1]
            w._day_wind_direction = day[1]["part"][0][1]["wind"][0][1]["d"][0][1]
            w._day_wind_direction_text = day[1]["part"][0][1]["wind"][0][1]["t"][0][1]
            w._day_humidity = day[1]["part"][0][1]["hmid"][0][1]
            w._day_precipitation_chance = day[1]["part"][0][1]["ppcp"][0][1]

            w._night_weather_desc = day[1]["part"][1][1]["t"][0][1]
            w._night_wind_speed = day[1]["part"][1][1]["wind"][0][1]["s"][0][1]
            w._night_wind_direction = day[1]["part"][1][1]["wind"][0][1]["d"][0][1]
            w._night_wind_direction_text = day[1]["part"][1][1]["wind"][0][1]["t"][0][1]
            w._night_humidity = day[1]["part"][1][1]["hmid"][0][1]
            w._night_precipitation_chance = day[1]["part"][1][1]["ppcp"][0][1]
            weathers.append(w)

        return weathers

    @property
    def latestUpdateTime(self):
        return self._latestUpdateTime

    @property
    def date(self):
        return "%s, %s" % (self._day, self._date)

    @property
    def temperature(self):
        return "%s/%s %s" % ("--" if self._tmp_lowest is None else self._tmp_lowest,
                                "--" if self._tmp_highest is None else self._tmp_highest,self._unit_tmp)

    @property
    def sunrise(self):
        return self._sunrise

    @property
    def sunset(self):
        return self._sunset

    @property
    def dayWeather(self):
        return self._day_weather_desc

    @property
    def dayWind(self):
        return "%s %s %s " % (self._day_wind_direction_text, self._day_wind_speed, self._unit_speed)

    @property
    def dayHumidity(self):
        return "%s%%" % (self._day_humidity)

    @property
    def dayPerciChance(self):
        return "%s%%" % (self._day_precipitation_chance)

    @property
    def nightWeather(self):
        return self._night_weather_desc

    @property
    def nightWind(self):
        return "%s %s %s " % (self._night_wind_direction_text, self._night_wind_speed, self._unit_speed)

    @property
    def nightHumidity(self):
        return "%s%%" % (self._night_humidity)

    @property
    def nightPerciChance(self):
        return "%s%%" % (self._night_precipitation_chance)


class ComWeather(object):
    searchApi = "http://wxdata.weather.com/wxdata/search/search?where=%s&locale=%s"

    def __init__(self, city_id, location, lang):
        self.city_id = city_id
        self.location = location
        self.lang = lang
        self.weatherApi = "http://wxdata.weather.com/wxdata/weather/local/%s?locale=%s" % (city_id, lang)

    @classmethod
    def search(cls, keyword, lang="en_US"):
        data = requests.get(cls.searchApi % (keyword, lang)).text
        tree = ET.XML(data)  # type: ET.Element
        if len(tree) == 0:
            return None
        for cNode in list(tree):  # type: ET.Element
            return cls(cNode.get("id"), cNode.text, lang)

    def getCurrent(self):
        api = self.weatherApi + "&cc"
        data = requests.get(api).text
        tree = ET.XML(data)  # type: ET.Element
        for cNode in list(tree):
            if cNode.tag == "cc":
                return _ComWeatherCurrent.initFromXML(cNode)

    def getDays(self, dayf=1):
        api = self.weatherApi + "&dayf=%s" % dayf
        data = requests.get(api).text
        tree = ET.XML(data)  # type: ET.Element
        for cNode in list(tree):
            if cNode.tag == "dayf":
                return _ComWeatherDay.initFromXML(cNode)


class WeatherCurrent:
    def __init__(self, json_node, minutely, intensity_threshold=0.05, prob_threshold=0.30):
        self.summary = json_node['summary']
        self.icon = json_node['fog']

        self.temperature = json_node['temperature']
        self.apparentTemperature = json_node['apparentTemperature']
        self.dewPoint = json_node['dewPoint']
        self.humidity = json_node['humidity']
        self.windSpeed = json_node['windSpeed']
        self.windBearing = json_node['windBearing']
        self.uvIndex = json_node['uvIndex']
        self.visibility = json_node['visibility']

        self.next_precip_change_time = None
        self.next_precip_change_intensity = None
        self.next_precip_change_prob = None

        # process minutely
        data = minutely['data']
        intensity = data[0]['precipIntensity']

        for minute in data:
            if abs(intensity - minute['precipIntensity']) > intensity_threshold and \
                minute['precipProbability'] > prob_threshold:
                self.next_precip_change_time = minute['time']
                self.next_precip_change_intensity = minute['precipIntensity']
                self.next_precip_change_prob = minute['precipProbability']


class WeatherDay:
    def __init__(self, day_node):
        self.temperatureMin = day_node['apparentTemperatureMin']
        self.apparentTemperatureMin = day_node['temperatureMin']
        self.temperatureMax = day_node['temperatureMax']
        self.apparentTemperatureMax = day_node['apparentTemperatureMax']
        self.dewPoint = day_node['dewPoint']
        self.humidity = day_node['humidity']
        self.windSpeed = day_node['windSpeed']
        self.windBearing = day_node['windBearing']
        self.precipIntensity = day_node['precipIntensity']
        self.precipProbability = day_node['precipProbability']
        self.precipType = day_node['precipType']
        self.uvIndex = day_node['uvIndex']
        self.visibility = day_node['visibility']
        self.sunriseTime = day_node['sunriseTime']
        self.sundownTime = day_node['sunsetTime']
        self.moonPhase = day_node['moonPhase']


class WeatherHour:
    def __init__(self, hourly_node):
        self.temperature = hourly_node['temperature']
        self.apparentTemperature = hourly_node['apparentTemperature']
        self.precipIntensity = hourly_node['precipIntensity']
        self.precipProbability = hourly_node['precipProbability']
        self.humidity = hourly_node['humidity']
        self.uvIndex = hourly_node['uvIndex']
        self.visibility = hourly_node['visibility']
        self.windSpeed = hourly_node['windSpeed']


class Weather:
    def __init__(self, response):
        self.timezone = response['timezone']
        self.latitude = response['latitude']
        self.longitude = response['longitude']

        self.current = WeatherCurrent(response['current'], response['minutely'])

        self.minute_summary = response['minutely']['summary']
        self.minute_icon = response['minutely']['icon']

        self.hourly_summary = response['hourly']['summary']
        self.hourly_icon = response['hourly']['icon']
        self.hourly = [WeatherHour(x) for x in response['hourly']['data']]

        self.daily_summary = response['daily']['summary']
        self.daily_icon = response['daily']['icon']
        self.daily = [WeatherDay(x) for x in response['daily']['data']]
