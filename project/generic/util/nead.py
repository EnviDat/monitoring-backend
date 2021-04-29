from django.http import HttpResponseNotFound
from pathlib import Path


# ----------------------------------------  NEAD Config Router --------------------------------------------------------
def nead_config_router(app):

    nead_config = ''

    if app == 'gcnet':
        nead_config = Path('gcnet/config/nead_header.ini')

    # # Else use generic stream
    # else:
    #     # Create the streaming response object and output csv
    #     response = StreamingHttpResponse(stream(version, hash_lines, model_class, display_values,
    #                                             nodata, start, end, dict_fields), content_type='text/csv')
    #     response['Content-Disposition'] = 'attachment; filename=' + output_csv

    # Check if nead_config exists
    if not nead_config:
        return HttpResponseNotFound("<h1>Not found: NEAD config doesn't exist for app {0}</h1>".format(app))

    print(nead_config)
    return nead_config




# ----------------------------------------  NEAD Config Writer --------------------------------------------------------
def write_nead_config(app, nead_header, model, parentclass, header_symbol):

    header = nead_header
    config = '{0}/nead_config/{1}/{2}.ini'.format(app, parentclass, model)
    bom = 'ï»¿'

    with open(config, 'w', newline='', encoding="utf-8-sig") as sink:
        for line in header:
            sink.write(line.lstrip(bom).lstrip(header_symbol).lstrip())