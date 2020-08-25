from pathlib import Path
import configparser


def read_config(config_path: str):
    config_file = Path(config_path)

    # Load configuration file
    config = configparser.ConfigParser()
    config.read(config_file)

    print("Read config params file: {0}, sections: {1}".format(config_path, ', '.join(config.sections())))

    if len(config.sections()) < 1:
        print("Invalid config file, has 0 sections")
        return None

    return config
