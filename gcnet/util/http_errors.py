# =================================  HTTP ERROR RESPONSES =============================================================


from django.http import HttpResponseNotFound


def model_http_error(model):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                "<h3>Valid models are listed at: "
                                "<a href=https://www.envidat.ch/data-api/gcnet/models/ target=_blank>"
                                "https://www.envidat.ch/data-api/gcnet/models/</a></h3>".format(model))


def parameter_http_error(parameter):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid parameter entered in URL: {0}</h3>"
                                "<h3>Valid parameters are:</h3>"
                                "<p>swin, swin_maximum, swout, swin_stdev, netrad, netrad_stdev, airtemp1, airtemp1_maximum,"
                                " airtemp1_minimum, airtemp2, airtemp2_maximum, airtemp2_minimum, airtemp_cs500air1, "
                                "airtemp_cs500air2, rh1, rh2, windspeed1, windspeed_u1_maximum, windspeed_u1_stdev,"
                                "windspeed2, windspeed_u2_maximum, windspeed_u2_stdev, winddir1, winddir2, pressure,"
                                " sh1, sh2, battvolt, reftemp"
                                .format(parameter))


def timestamp_meaning_http_error(timestamp_meaning):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                .format(timestamp_meaning))


def station_http_error():
    return HttpResponseNotFound("<h1>Not found: station config doesn't exist</h1>")


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
