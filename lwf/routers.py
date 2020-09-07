from lwf.models.LWFMeteoTest import LWFMeteoTest

LWF_MODEL = [LWFMeteoTest]


class MonitoringRouter:

    #monitoring_label = {'monitoring'}

    def db_for_read(self, model):

        # model_obj = model.objects.create()
        # obj_content_type = ContentType.objects.get_for_models(model_obj)
        # print(obj_content_type.app_label)

        # if model.startswith == 'monitoring':
        # if model.app_label == 'monitoring':
        #     print('***USING LWF SCHEMA***')
        #     return 'lwf'
        # print('***USING PUBLIC SCHEMA***')
        return 'lwf'

    def db_for_write(self, model, **hints):

        #print('TEST  ' + model._meta.app_label)

        # # if model._meta.app_label is self.monitoring_label:
        # if model in LWF_MODEL:
        #     #print(model.app_label)
        #     print('***USING LWF SCHEMA***')
        #     return 'lwf'
        # print('***USING PUBLIC SCHEMA***')
        return 'lwf'
