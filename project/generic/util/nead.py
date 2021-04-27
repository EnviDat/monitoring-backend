

def write_nead_config(app, nead_header, model, parentclass, header_symbol):

    header = nead_header
    config = '{0}/nead_config/{1}/{2}.ini'.format(app, parentclass, model)
    bom = 'ï»¿'

    with open(config, 'w', newline='', encoding="utf-8-sig") as sink:
        for line in header:
            sink.write(line.lstrip(bom).lstrip(header_symbol).lstrip())