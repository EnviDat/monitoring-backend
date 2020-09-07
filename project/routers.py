

class MonitoringRouter:

    #monitoring_label = {'monitoring'}

    def db_for_read(self, model):
        #print("APP_LABEL " + model._meta.app_label)
        if model._meta.app_label == 'lwf':
            return 'lwf'
        else:
            print('WARNING (routers.py) non-valid model": {0}'.format(model))
            return -1



