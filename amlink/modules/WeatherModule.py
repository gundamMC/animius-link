def weather_look_up(name_entity_data, user_id):
    # parse NER data to get exact query
    # and then return according response
    # using self.location and self.weather
    print(user_id, 'user called :', name_entity_data)


register_intents = {
    'weather': weather_look_up
}
