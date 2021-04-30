from pathlib import Path
from io import StringIO


# ----------------------------------------  NEAD Config Writer --------------------------------------------------------
from project.generic.util.views_helpers import read_config


def write_nead_config(app, nead_header, model, parent_class, header_symbol):
    header = nead_header
    config = f'{app}/nead_config/{parent_class}/{model}.ini'
    bom = 'ï»¿'

    with open(config, 'w+', newline='', encoding="utf-8-sig") as sink:
        for line in header:
            sink.write(line.lstrip(bom).lstrip(header_symbol).lstrip().rstrip(','))




# ----------------------------------------  Get NEAD Config -----------------------------------------------------------
def get_nead_config(app, **kwargs):

    model = kwargs['model']
    parent_class= kwargs['parent_class']

    nead_config = Path(f'{app}/nead_config/{parent_class}/{model}.ini')

    # Check if nead_config exists
    if nead_config.exists():
        return nead_config

    return ''


def get_config_list(config_path):

    config_list =[]

    with open(config_path, 'r', encoding="utf-8-sig") as config:
        for line in config:
            config_list.append(line)

    return config_list






    # # Get header config
    # config = read_config(config_path)

    # config_buffer = open(config_path, 'r')
    #
    # # # Dynamically write NEAD header into buffer_
    # # buffer_ = StringIO()
    # # config.write(buffer_)
    # print(config_buffer.readlines())
    #
    # return config_buffer


