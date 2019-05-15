import WeatherModel
from WeatherModel import ComWeather

city = ComWeather.search("shanghai")
w = city.getCurrent()  # type: WeatherModel._WeatherCurrent
print(w.latestUpdateTime)
print(w.pressure)
print(w.temperature)
print(w.weather)
print(w.humidity)
wd = city.getDays(dayf=2)[1] # type: WeatherModel._WeatherDay
print(wd.date)
print(wd.dayWeather)
print(wd.dayWind)
print(wd.dayPerciChance)
print(wd.nightPerciChance)
print(wd.nightHumidity)
print(wd.temperature)