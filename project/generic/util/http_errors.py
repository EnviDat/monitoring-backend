from django.http import HttpResponseNotFound


def timestamp_http_error():
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Incorrect date format for 'start' and/or 'end' timestamps.</h3>"
                                "<h3>Start and end dates should both be in ISO timestamp "
                                "date and time format: YYYY-MM-DDTHH:MM:SS ('2020-10-20T17:00:00')</h3>")


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
                                    "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>".format(model))


