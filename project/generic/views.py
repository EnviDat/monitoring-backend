from django.http import JsonResponse

from project.generic.util.views_helpers import get_models_list


# View returns a list of models currently in an app
def get_models(request, app):
    models = get_models_list(app)
    return JsonResponse(models, safe=False)