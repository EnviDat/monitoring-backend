from django.http import HttpResponseNotFound


# =================================  HTTP ERROR RESPONSES =============================================================

def model_http_error(model):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                "<h3>Valid models are listed at: "
                                "<a href=https://www.envidat.ch/data-api/lwf/models/ target=_blank>"
                                "https://www.envidat.ch/data-api/lwf/models/</a></h3>".format(model))


def parameter_http_error(parameter):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>No valid parameter(s) entered in URL: {0}</h3>"
                                "<h3>Valid parameters are:</h3>"
                                "<p>air_temperature_10, precipitation_60, precipitation_10, precipitation_10_multi,"
                                "precipitation_60_multi, wind_speed_10, wind_speed_max_10, wind_direction_10, "
                                "relative_air_humidity_60, relative_air_humidity_10, global_radiation_10, "
                                "photosynthetic_active_radiation_10, uv_b_radiation_10, vapour_pressure_deficit_10,"
                                " dewpoint_10, ozone_10, soil_temperature_60_5, soil_temperature_60_10, "
                                "soil_temperature_60_20, soil_temperature_10_5, soil_temperature_10_10, "
                                "soil_temperature_10_30, soil_temperature_10_50, soil_temperature_10_80, "
                                "soil_temperature_10_120, soil_temperature_20_15, soil_temperature_20_50, "
                                "soil_temperature_20_80, soil_temperature_20_150, soil_water_potential_20_15, "
                                "soil_water_potential_20_50, soil_water_potential_20_80, "
                                "soil_water_potential_20_150, soil_water_content_60_15, soil_water_content_60_50, "
                                "soil_water_content_60_80, soil_water_content_60_5, soil_water_content_60_30,"
                                "soil_water_content_10_15, soil_water_content_10_50, soil_water_content_10_80"
                                .format(parameter))
