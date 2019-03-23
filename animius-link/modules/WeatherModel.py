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

    def init_dark_sky(self, response):

        self.current = WeatherCurrent()
        self.current.init_dark_sky(response['currently'], response['minutely'])

        self.minute_summary = response['minutely']['summary']
        self.minute_icon = response['minutely']['icon']

        self.hourly_summary = response['hourly']['summary']
        self.hourly_icon = response['hourly']['icon']
        self.hourly = [WeatherHour().init_dark_sky(x) for x in response['hourly']['data']]

        self.daily_summary = response['daily']['summary']
        self.daily_icon = response['daily']['icon']
        self.daily = [WeatherDay().init_dark_sky(x) for x in response['daily']['data']]

        return self

    def init_weather_com(self, response):
        tree = ET.XML(response)  # type: ET.Element

        self.current = WeatherCurrent()
        self.current.init_weather_com(tree.find('cc'))

        daily_node = nodetextToDict(tree.find('dayf'))
        self.daily = []
        for day in daily_node["day"]:
            weather_day = WeatherDay()
            weather_day.init_weather_com(day)
            self.daily.append(weather_day)

        return self


class Location:

    weather_com_api = "http://wxdata.weather.com/wxdata/weather/local/%s?unit=%s&locale=%s&cc&dayf=%s"
    weather_com_search = "http://wxdata.weather.com/wxdata/search/search?where=%s&locale=%s"
    dark_sky_api = "https://api.darksky.net/forecast/%s/%s,%s?units=%s&lang=%s"

    def __init__(self):
        self.com_id = None
        self.latitude = None
        self.longitude = None

        self.locale = "en"  # TODO: Make locale automatically change between dark sky and weather.com
        self.si_units = False

        self.dark_sky_key = None

    def search(self, keyword):
        data = requests.get(Location.weather_com_search % (keyword, self.locale)).text
        tree = ET.XML(data)  # type: ET.Element
        if len(tree) == 0:
            return None

        results = {}

        for cNode in list(tree):  # type: ET.Element
            results[cNode.text] = cNode.get("id")

        return results

    def select(self, com_id):
        self.com_id = com_id

    def get_weather_com(self, weather):
        response = requests.get(Location.weather_com_api % (self.com_id, 'm' if self.si_units else 'f', self.locale, 8)).text
        weather.init_weather_com(response)

    def get_dark_sky(self, weather):

        if self.latitude is None or self.longitude is None:
            # find latitude and longitude using weather.com's api.
            weather_com_response = requests.get(Location.weather_com_api % (self.com_id, 'm' if self.si_units else 'f', self.locale, 8)).text
            tree = ET.XML(weather_com_response)  # type: ET.Element
            loc = tree.find('loc')
            self.com_id = loc.get('id')
            self.longitude = loc.find('lon').text
            self.latitude = loc.find('lat').text

        response = requests.get(Location.dark_sky_api % (self.dark_sky_key,
                                                         self.latitude,
                                                         self.longitude,
                                                         ('si' if self.si_units else 'us'),
                                                         self.locale)).json()
        weather.init_dark_sky(response)


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

    def init_dark_sky(self, json_node, minutely, intensity_threshold=0.05, prob_threshold=0.30):
        self.summary = json_node['summary']
        self.icon = json_node['icon']

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

        return self

    def init_weather_com(self, xml_node):
        node = nodetextToDict(xml_node)
        self.temperature = node["tmp"][0][1]
        self.apparentTemperature = node["flik"][0][1]
        self.summary = node["t"][0][1]
        self.icon = self.summary
        self.dewPoint = node["dewp"][0][1]
        self.humidity = node["hmid"][0][1]
        self.visibility = node["vis"][0][1]
        self.windSpeed = node["wind"][0][1]["s"][0][1]
        self.windBearing = node["wind"][0][1]["d"][0][1]
        self.uvIndex = node["uv"][0][1]["i"][0][1]

        # no minutely data for weather.com

        return self


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

    def init_dark_sky(self, day_node):
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

        return self

    def init_weather_com(self, day):

        self.temperatureMax = day[1]["hi"][0][1]
        self.temperatureMin = day[1]["low"][0][1]
        self.sunriseTime = day[1]["sunr"][0][1]
        self.sundownTime = day[1]["suns"][0][1]

        self.windSpeed = day[1]["part"][0][1]["wind"][0][1]["s"][0][1]
        self.windBearing = day[1]["part"][0][1]["wind"][0][1]["d"][0][1]
        self.humidity = day[1]["part"][0][1]["hmid"][0][1]
        self.precipProbability = day[1]["part"][0][1]["ppcp"][0][1]

        return self


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

    def init_dark_sky(self, hourly_node):
        self.temperature = hourly_node['temperature']
        self.apparentTemperature = hourly_node['apparentTemperature']
        self.precipIntensity = hourly_node['precipIntensity']
        self.precipProbability = hourly_node['precipProbability']
        self.humidity = hourly_node['humidity']
        self.uvIndex = hourly_node['uvIndex']
        self.visibility = hourly_node['visibility']
        self.windSpeed = hourly_node['windSpeed']

        return self


test_loc = Location()
print(test_loc.search('San fran'))

test_loc.select('USCA0987')

test_weather = Weather()

test_loc.dark_sky_key = "enter key here"

test_loc.get_dark_sky(test_weather)

print('end')