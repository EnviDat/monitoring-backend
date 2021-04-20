from django.apps import apps


# Function returns a list of models in an app
def get_models_list(app):
    models = []
    for key in apps.all_models[app]:
        models.append(key)
    return models