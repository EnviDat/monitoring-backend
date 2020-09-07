class MonitoringRouter:
    route_app_labels = {'lwf'}

    def db_for_read(self, model):
        if model._meta.app_label == 'lwf':
            return 'lwf'
        else:
            print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1

    def db_for_write(self, model):
        if model._meta.app_label in self.route_app_labels:
            return model._meta.app_label
        else:
            print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1
