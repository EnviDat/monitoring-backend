

class MonitoringRouter:
    route_app_labels = {'lwf', 'gcnet'}

    def db_for_read(self, model):
        if model._meta.app_label == 'lwf':
            return 'lwf'
        elif model._meta.app_label == 'gcnet':
            return 'gcnet'
        else:
            print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1

    def db_for_write(self, model, **kwargs):
        if model._meta.app_label == 'lwf':
            # print("APP_LABEL: " + model._meta.app_label)
            return 'lwf'
        elif model._meta.app_label == 'gcnet':
            # print("APP_LABEL: " + model._meta.app_label)
            return 'gcnet'
        else:
            # print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1

    def allow_migrate(self, db, app_label, model_name=None, **hints):
            # return 'gcnet'
        if app_label == 'lwf':
            # print("APP_LABEL: " + app_label)
            return 'lwf'
        elif app_label == 'gcnet':
            # print("APP_LABEL: " + app_label)
            return 'gcnet'
        else:
            # print('WARNING (routers.py) non-valid app_label": {0}'.format(app_label))
            return -1
