import toml
from mergedeep import merge, Strategy

def exception(msg, e, logger=None):
    print("ERROR:", msg, "\nException: " + str(e)) if logger is None else logger.error(msg, exc_info=e)

def read_config(file, default_config, logger=None):
    try:
        with open(file, "r") as config_file:
            config = toml.load(config_file)
    except FileNotFoundError as e:
        exception(f"{file} not found, falling back to defaults", e, logger=logger)
        return default_config
    except Exception as e:
        exception(f"could not load {file}, falling back to defaults", e, logger=logger)
        return default_config
    
    # Deep merge default_config with config
    try:
        merged = merge(default_config, config, strategy=Strategy.TYPESAFE_REPLACE)
    except Exception as e:
        exception(f"could not merge config dictionaries, falling back to defaults", e, logger=logger)
        return default_config
    
    return merged