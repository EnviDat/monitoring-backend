from django.http import HttpResponseNotFound


def timestamp_http_error():
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                "<h3>Start and end dates should both be in ISO timestamp "
                                "date and time format: YYYY-MM-DDTHH:MM:SS ('2020-10-20T17:00:00')</h3>")


def date_http_error():
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                "<h3>Start and end dates should both be in either ISO timestamp "
                                "date format: YYYY-MM-DD ('2019-12-04')</h3>")


def model_http_error(model, app):
    if app == 'gcnet':
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                    "<h3>Valid models are listed at: "
                                    "<a href=https://www.envidat.ch/data-api/gcnet/models/ target=_blank>"
                                    "https://www.envidat.ch/data-api/gcnet/models/</a></h3>".format(model))
    # TODO implement URL in error response
    elif app == 'lwf':
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                    "<h3>Valid models are listed at: "
                                    "<a href=https://www.envidat.ch/data-api/lwf/models/ target=_blank>"
                                    "https://www.envidat.ch/data-api/lwf/models/</a></h3>".format(model))
    else:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>Non-valid 'model' entered in URL: {0}</h3>".format(model))


def parameter_http_error(parameter, app, parent_class):
    if app == 'gcnet':
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>No valid parameter(s) entered in URL: {0}</h3>"
                                    "<h3>Valid parameters are:</h3>"
                                    "<p>swin, swin_maximum, swout, swout_minimum, netrad, netrad_maximum, airtemp1, airtemp1_maximum,"
                                    " airtemp1_minimum, airtemp2, airtemp2_maximum, airtemp2_minimum, airtemp_cs500air1, "
                                    "airtemp_cs500air2, rh1, rh2, windspeed1, windspeed_u1_maximum, windspeed_u1_stdev,"
                                    "windspeed2, windspeed_u2_maximum, windspeed_u2_stdev, winddir1, winddir2, pressure,"
                                    " sh1, sh2, battvolt, reftemp"
                                    .format(parameter))
    elif parent_class == 'LWFStation':
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
    else:
        return HttpResponseNotFound("<h1>Page not found</h1>"
                                    "<h3>No valid parameter(s) entered in URL: {0}</h3>"
                                    .format(parameter))
