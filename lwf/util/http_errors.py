from django.http import HttpResponseNotFound


# =================================  HTTP ERROR RESPONSES =============================================================

def model_http_error(model):
    return HttpResponseNotFound("<h1>Page not found</h1>"
                                "<h3>Non-valid 'model' (station) entered in URL: {0}</h3>"
                                "<h3>Valid models are listed at: "
                                "<a href=https://www.envidat.ch/data-api/lwf/models/ target=_blank>"
                                "https://www.envidat.ch/data-api/lwf/models/</a></h3>".format(model))
