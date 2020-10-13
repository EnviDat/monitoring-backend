import importlib
from django.core.exceptions import FieldError
from django.db.models import Avg, Max, Min, Sum
from django.http import JsonResponse

from lwf.helpers import get_timestamp_iso_range_dict, Round2, get_lwf_models_list, get_timestamp_iso_range_day_dict, \
    get_timestamp_iso_range_year_week, get_timestamp_iso_range_years


# View returns a list of models currently in the 'lwf' app
def get_lwf_models(request):
    lwf_models = get_lwf_models_list()
    return JsonResponse(lwf_models, safe=False)


# User customized view that returns data based on level of detail and parameter specified by
# model (i.e. 'database_station_name' in conf file)
# Levels of detail:  'all' (every hour), 'quarterday' (00:00, 06:00, 12:00, 18:00), 'halfday' (00:00, 12:00)
# Accepts ISO timestamp ranges
def get_db_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']

    display_values = ['timestamp_iso', parameter]

    # Check if 'start' and 'end' kwargs are in both ISO timestamp format, assign filter to timestamp_iso field range
    dict_timestamps = get_timestamp_iso_range_dict(start, end)

    # Get the model
    class_name = model.rsplit('.', 1)[-1]
    package = importlib.import_module("lwf.models")
    model_class = getattr(package, class_name)

    if lod == 'quarterday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(quarterday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} quarterday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    elif lod == 'halfday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(halfday=True)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} halfday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    elif lod == 'all':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(**dict_timestamps)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} all url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    else:
        raise FieldError("Incorrect values inputted in url")


# Returns derived data values by day, week, or year: 'avg' (average), 'max' (maximum) and 'min' (minimum)
# User customized view that returns data based parameter specified
# lod must be 'day', 'week', or 'year'
# calc must be 'avg', 'max', 'min', or 'sum'
# Accepts ISO timestamp ranges
def get_derived_data(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']
    calc = kwargs['calc']

    dict_avg = {parameter + '_avg': Round2(Avg(parameter))}
    dict_max = {parameter + '_max': Max(parameter)}
    dict_min = {parameter + '_min': Min(parameter)}
    # dict_sum = {parameter + '_sum': Round2(Sum(parameter))}

    # Check if 'start' and 'end' kwargs are in both ISO timestamp format, assign filter to timestamp_iso field range
    #dict_timestamps = get_timestamp_iso_range_dict(start, end)

    # Check which level of detail was passed
    # TODO verify this is ok and also implement in GC-Net app?
    # Check if timestamps are in whole date format: YYYY-MM-DD ('2019-12-04')
    if lod == 'day':
        dict_timestamps = get_timestamp_iso_range_day_dict(start, end)
        print(dict_timestamps)
    # Check if timestamps are in whole week format: YYYY-WW ('2020-22')  ('22' is the twenty-second week of the year)
    elif lod == 'week':
        dict_timestamps = get_timestamp_iso_range_year_week(start, end)
        print(dict_timestamps)
    # Check if timestamps are in whole year format: YYYY ('2020')
    elif lod == 'year':
        dict_timestamps = get_timestamp_iso_range_years(start, end)
        print(dict_timestamps)
    else:
        raise FieldError("Incorrect values inputted in 'lod' url")

    # Get the model
    class_name = model.rsplit('.', 1)[-1]
    package = importlib.import_module("lwf.models")
    model_class = getattr(package, class_name)

    if calc == 'avg':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_avg)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'avg' url")
        return JsonResponse(queryset, safe=False)

    elif calc == 'max':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_max)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'max' url")
        return JsonResponse(queryset, safe=False)

    elif calc == 'min':
        try:
            queryset = list(model_class.objects
                            .values(lod)
                            .annotate(**dict_min)
                            .filter(**dict_timestamps)
                            .order_by(lod))
        except FieldError:
            raise FieldError("Incorrect values inputted in 'min' url")
        return JsonResponse(queryset, safe=False)

    # elif calc == 'sum':
    #     try:
    #         queryset = list(model_class.objects
    #                         .values(lod)
    #                         .annotate(**dict_sum)
    #                         .filter(**dict_timestamps)
    #                         .order_by(lod))
    #     except FieldError:
    #         raise FieldError("Incorrect values inputted in 'sum' url")
    #     return JsonResponse(queryset, safe=False)

    else:
        raise FieldError("Incorrect values inputted in url")


# View similar to get_db_data() but offers additional filtering by returning values greater than a specified filter
# Note only returns values > x (not inclusive of x!)
# User customized view that returns data based on level of detail and parameter specified by
# model (i.e. 'database_station_name' in conf file)
# Levels of detail:  'all' (every hour), 'quarterday' (00:00, 06:00, 12:00, 18:00), 'halfday' (00:00, 12:00)
# Accepts ISO timestamp ranges
# Values returned are greater than value specified in 'gt'
def get_db_data_greater_than(request, **kwargs):
    # Assign kwargs from url to variables
    start = kwargs['start']
    end = kwargs['end']
    lod = kwargs['lod']
    parameter = kwargs['parameter']
    model = kwargs['model']
    greater_than = kwargs['gt']

    display_values = ['timestamp_iso', parameter]

    # Assign greater_than filter to dict_greater_than
    dict_greater_than = {parameter + '__gt': greater_than}

    # Check if 'start' and 'end' kwargs are in both ISO timestamp format, assign filter to timestamp_iso field range
    dict_timestamps = get_timestamp_iso_range_dict(start, end)

    # Get the model
    class_name = model.rsplit('.', 1)[-1]
    package = importlib.import_module("lwf.models")
    model_class = getattr(package, class_name)

    if lod == 'quarterday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(quarterday=True)
                            .filter(**dict_timestamps)
                            .filter(**dict_greater_than)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} quarterday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    elif lod == 'halfday':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(halfday=True)
                            .filter(**dict_timestamps)
                            .filter(**dict_greater_than)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} halfday url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    elif lod == 'all':
        try:
            queryset = list(model_class.objects
                            .values(*display_values)
                            .filter(**dict_timestamps)
                            .filter(**dict_greater_than)
                            .order_by('timestamp_iso').all())
        except FieldError:
            raise FieldError('Incorrect values inputted in {0} all url parameter'.format(model))
        return JsonResponse(queryset, safe=False)

    else:
        raise FieldError("Incorrect values inputted in url")