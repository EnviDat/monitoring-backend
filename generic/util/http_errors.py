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


def model_http_error(model):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'model' entered in URL: {0}</h3>".format(model))


def parent_class_http_error(parent_class):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'parent_class' entered in URL: {0}</h3>".format(parent_class))


def parameter_http_error(parameter):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>No valid parameter(s) entered in URL: {0}</h3>"
                                .format(parameter))


def timestamp_meaning_http_error(timestamp_meaning):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'timestamp_meaning' kwarg entered in URL: {0}</h3>"
                                "<h3>Valid 'timestamp_meaning' kwarg options: end, beginning"
                                .format(timestamp_meaning))
