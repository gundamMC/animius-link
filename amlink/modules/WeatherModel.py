from xml.etree import ElementTree as ET

import requests


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


class Weather:
    def __init__(self):
        self.current = None

        self.minute_summary = None
        self.minute_icon = None

        self.hourly_summary = None
        self.hourly_icon = None
        self.hourly = None

        self.daily_summary = None
        self.daily_icon = None
        self.daily = None

    @classmethod
    def init_dark_sky(cls, response):
        w = cls()
        w.current = WeatherCurrent.init_dark_sky(response['currently'], response['minutely'])

        w.minute_summary = response['minutely']['summary']
        w.minute_icon = response['minutely']['icon']

        w.hourly_summary = response['hourly']['summary']
        w.hourly_icon = response['hourly']['icon']
        w.hourly = [WeatherHour.init_dark_sky(x) for x in response['hourly']['data']]

        w.daily_summary = response['daily']['summary']
        w.daily_icon = response['daily']['icon']
        w.daily = [WeatherDay.init_dark_sky(x) for x in response['daily']['data']]

        return w

    @classmethod
    def init_weather_com(cls, response):
        w = cls()
        tree = ET.XML(response)  # type: ET.Element

        w.current = WeatherCurrent.init_weather_com(tree.find('cc'))

        daily_node = nodetextToDict(tree.find('dayf'))
        w.daily = [WeatherDay.init_weather_com(day) for day in daily_node["day"]]
        return w


class WeatherLocation:
    weather_com_api = "https://wxdata.weather.com/wxdata/weather/local/%s?unit=%s&locale=%s&cc&dayf=%s"
    weather_com_search = "https://wxdata.weather.com/wxdata/search/search?where=%s&locale=%s"
    dark_sky_api = "https://api.darksky.net/forecast/%s/%s,%s?units=%s&lang=%s"

    def __init__(self, dark_sky_key=None):
        self.com_id = None
        self.latitude = None
        self.longitude = None

        self.locale = "en"
        # TODO: Make locale automatically change between dark sky and weather.com maybe map a dict?
        self.si_units = False

        self.dark_sky_key = dark_sky_key

    def search(self, keyword):
        data = requests.get(self.weather_com_search % (keyword, self.locale)).text
        tree = ET.XML(data)  # type: ET.Element
        if len(tree) == 0:
            return None

        results = {}

        for cNode in list(tree):  # type: ET.Element
            results[cNode.text] = cNode.get("id")

        return results

    def select(self, com_id):
        self.com_id = com_id

    def get_weather_com(self):
        response = requests.get(
            self.weather_com_api % (self.com_id, 'm' if self.si_units else 'f', self.locale, 8)).text
        return Weather.init_weather_com(response)

    def get_dark_sky(self):
        # Please don't move this to select. Show some love for the people
        #  that are using weather.com (One less API call)
        if self.latitude is None or self.longitude is None:
            # find latitude and longitude using weather.com's api.
            weather_com_response = requests.get(
                self.weather_com_api % (self.com_id, 'm' if self.si_units else 'f', self.locale, 8)).text
            tree = ET.XML(weather_com_response)  # type: ET.Element
            loc = tree.find('loc')
            self.com_id = loc.get('id')
            self.longitude = loc.find('lon').text
            self.latitude = loc.find('lat').text

        response = requests.get(self.dark_sky_api % (self.dark_sky_key,
                                                     self.latitude,
                                                     self.longitude,
                                                     ('si' if self.si_units else 'us'),
                                                     self.locale)).json()
        return Weather.init_dark_sky(response)

    def get(self):  # no pref over weather.com and dark sky
        if self.dark_sky_key is not None:
            return self.get_dark_sky()
        else:
            return self.get_weather_com()


class WeatherCurrent:

    def __init__(self):
        self.summary = None
        self.icon = None

        self.temperature = None
        self.apparentTemperature = None
        self.dewPoint = None
        self.humidity = None
        self.windSpeed = None
        self.windBearing = None
        self.uvIndex = None
        self.visibility = None

        self.next_precip_change_time = None
        self.next_precip_change_intensity = None
        self.next_precip_change_prob = None

    @classmethod
    def init_dark_sky(cls, json_node, minutely, intensity_threshold=0.05, prob_threshold=0.30):
        wc = cls()
        wc.summary = json_node['summary']
        wc.icon = json_node['icon']

        wc.temperature = json_node['temperature']
        wc.apparentTemperature = json_node['apparentTemperature']
        wc.dewPoint = json_node['dewPoint']
        wc.humidity = json_node['humidity']
        wc.windSpeed = json_node['windSpeed']
        wc.windBearing = json_node['windBearing']
        wc.uvIndex = json_node['uvIndex']
        wc.visibility = json_node['visibility']

        wc.next_precip_change_time = None
        wc.next_precip_change_intensity = None
        wc.next_precip_change_prob = None

        # process minutely
        data = minutely['data']
        intensity = data[0]['precipIntensity']

        for minute in data:
            if abs(intensity - minute['precipIntensity']) > intensity_threshold and \
                    minute['precipProbability'] > prob_threshold:
                wc.next_precip_change_time = minute['time']
                wc.next_precip_change_intensity = minute['precipIntensity']
                wc.next_precip_change_prob = minute['precipProbability']

        return wc

    @classmethod
    def init_weather_com(cls, xml_node):
        wc = cls()
        node = nodetextToDict(xml_node)
        wc.temperature = node["tmp"][0][1]
        wc.apparentTemperature = node["flik"][0][1]
        wc.summary = node["t"][0][1]
        wc.icon = wc.summary
        wc.dewPoint = node["dewp"][0][1]
        wc.humidity = node["hmid"][0][1]
        wc.visibility = node["vis"][0][1]
        wc.windSpeed = node["wind"][0][1]["s"][0][1]
        wc.windBearing = node["wind"][0][1]["d"][0][1]
        wc.uvIndex = node["uv"][0][1]["i"][0][1]

        # no minutely data for weather.com

        return wc


class WeatherDay:

    def __init__(self):
        self.temperatureMin = None
        self.apparentTemperatureMin = None
        self.temperatureMax = None
        self.apparentTemperatureMax = None
        self.dewPoint = None
        self.humidity = None
        self.windSpeed = None
        self.windBearing = None
        self.precipIntensity = None
        self.precipProbability = None
        self.precipType = None
        self.uvIndex = None
        self.visibility = None
        self.sunriseTime = None
        self.sundownTime = None
        self.moonPhase = None

    @classmethod
    def init_dark_sky(cls, day_node):
        wd = cls()
        wd.temperatureMin = day_node['apparentTemperatureMin']
        wd.apparentTemperatureMin = day_node['temperatureMin']
        wd.temperatureMax = day_node['temperatureMax']
        wd.apparentTemperatureMax = day_node['apparentTemperatureMax']
        wd.dewPoint = day_node['dewPoint']
        wd.humidity = day_node['humidity']
        wd.windSpeed = day_node['windSpeed']
        wd.windBearing = day_node['windBearing']
        wd.precipIntensity = day_node['precipIntensity']
        wd.precipProbability = day_node['precipProbability']
        wd.precipType = day_node['precipType']
        wd.uvIndex = day_node['uvIndex']
        wd.visibility = day_node['visibility']
        wd.sunriseTime = day_node['sunriseTime']
        wd.sundownTime = day_node['sunsetTime']
        wd.moonPhase = day_node['moonPhase']

        return wd

    @classmethod
    def init_weather_com(cls, day):
        wd = cls()
        wd.temperatureMax = day[1]["hi"][0][1]
        wd.temperatureMin = day[1]["low"][0][1]
        wd.sunriseTime = day[1]["sunr"][0][1]
        wd.sundownTime = day[1]["suns"][0][1]

        wd.windSpeed = day[1]["part"][0][1]["wind"][0][1]["s"][0][1]
        wd.windBearing = day[1]["part"][0][1]["wind"][0][1]["d"][0][1]
        wd.humidity = day[1]["part"][0][1]["hmid"][0][1]
        wd.precipProbability = day[1]["part"][0][1]["ppcp"][0][1]
        return wd


class WeatherHour:

    def __init__(self):
        self.temperature = None
        self.apparentTemperature = None
        self.precipIntensity = None
        self.precipProbability = None
        self.humidity = None
        self.uvIndex = None
        self.visibility = None
        self.windSpeed = None

    @classmethod
    def init_dark_sky(cls, hourly_node):
        wh = cls()
        wh.temperature = hourly_node['temperature']
        wh.apparentTemperature = hourly_node['apparentTemperature']
        wh.precipIntensity = hourly_node['precipIntensity']
        wh.precipProbability = hourly_node['precipProbability']
        wh.humidity = hourly_node['humidity']
        wh.uvIndex = hourly_node['uvIndex']
        wh.visibility = hourly_node['visibility']
        wh.windSpeed = hourly_node['windSpeed']

        return wh
