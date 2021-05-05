from django.apps import apps


# ----------------------------------------  New Model Helpers ---------------------------------------------------------

# Returns True if string has spaces
def has_spaces(string):
    if ' ' in string:
        return True
    else:
        return False


def model_exists(table_name):

    models = apps.all_models['lwf']
    model_names = list(models.keys())
    print(model_names)

    if table_name in model_names:
        return True
    else:
        return False
