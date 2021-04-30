from pathlib import Path


# ----------------------------------------  NEAD Config Writer --------------------------------------------------------
def write_nead_config(app, nead_header, model, parentclass, header_symbol):
    header = nead_header
    config = '{0}/nead_config/{1}/{2}.ini'.format(app, parentclass, model)
    bom = 'ï»¿'

    with open(config, 'w', newline='', encoding="utf-8-sig") as sink:
        for line in header:
            sink.write(line.lstrip(bom).lstrip(header_symbol).lstrip())


# ----------------------------------------  Get NEAD Config -----------------------------------------------------------
def get_nead_config(app, **kwargs):

    model = kwargs['model']
    parent_class= kwargs['parent_class']

    nead_config = Path('{0}/nead_config/{1}/{2}.ini'.format(app, parent_class, model))
    print(nead_config)

    # Check if nead_config exists
    if nead_config.exists():
        return nead_config

    return ''


