def weather_look_up(name_entity_data, user_id):
    # parse NER data to get exact query
    # and then return according response
    # using self.location and self.weather

    city = name_entity_data['city']
    time = name_entity_data['time']

    result = dict()

    return result


register_intents = {
    'weather': weather_look_up
}
