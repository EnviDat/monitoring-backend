from pathlib import Path
import configparser


# ------------------------------------------- Read Config ------------------------------------------------------------

def read_config(config_path: str):

    config_file = Path(config_path)

    # Load configuration file
    config = configparser.RawConfigParser(inline_comment_prefixes='#', allow_no_value=True)
    config.read(config_file)

    # print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(gc_config.sections())))

    if len(config.sections()) < 1:
        print("Invalid config file, missing sections")
        return None

    return config


# ----------------------------------------  NEAD Config Writer -------------------------------------------------------

# TODO fix right comma issue
def write_nead_config(app, nead_header, model, parent_class, header_symbol):
    header = nead_header
    config = f'{app}/nead_config/{parent_class}/{model}.ini'
    bom = 'ï»¿'

    # with open(config, 'w+', newline='', encoding="utf-8-sig") as sink:
    with open(config, 'w+', newline='', encoding="utf-8") as sink:
        for line in header:
            sink.write(line.lstrip(bom).lstrip(header_symbol).lstrip().rstrip(','))


# ----------------------------------------  Get NEAD Config -----------------------------------------------------------

def get_nead_config(app, **kwargs):
    model = kwargs['model']
    parent_class = kwargs['parent_class']

    nead_config = Path(f'{app}/nead_config/{parent_class}/{model}.ini')

    # Check if nead_config exists
    if nead_config.exists():
        return nead_config

    return ''


def get_config_list(config_path):
    config_list = []

    with open(config_path, 'r', encoding="utf-8-sig") as config:
        for line in config:
            config_list.append(line)

    return config_list


# Fill hash_lines with config_list lines prepended with '# '
def get_hashed_lines(config_list):
    hash_lines = []
    for line in config_list:
        line = '# ' + line
        hash_lines.append(line)
    return hash_lines


def get_database_fields(nead_config):
    nead_config_parser = read_config(nead_config)
    database_fields = nead_config_parser.get('FIELDS', 'database_fields')
    return database_fields

