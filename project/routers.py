

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

    def db_for_write(self, model):
        if model._meta.app_label == 'lwf':
            print("APP LABEL " + model._meta.app_label)
            return 'lwf'
        elif model._meta.app_label == 'gcnet':
            print("APP LABEL " + model._meta.app_label)
            return 'gcnet'
        else:
            print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1
        # if model._meta.app_label in self.route_app_labels:
        #     print("APP LABEL " + model._meta.app_label)
        #     return model._meta.app_label
        # else:
        #     print('WARNING (routers.py) non-valid model": {0}'.format(model))
        #     return -1
        # return 'lwf'

