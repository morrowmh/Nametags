import toml
from logging import Logger
from typing import Any

def exception(msg: str, e: Exception, logger: Logger=None) -> None:
    print("ERROR:", msg, "\nException:" + str(e)) if logger is None else logger.error(msg, exc_info=e)

def read_config(file: str, default_config: dict[str, Any], logger: Logger=None) -> dict[str, Any]:
    try:
        with open(file, "r") as config_file:
            config = toml.load(config_file)
    except FileNotFoundError as e:
        exception(f"{file} not found, generating default config", e, logger=logger)

        # Generate default config
        try:
            with open(file, "w") as config_file:
                toml.dump(default_config, config_file)
        except Exception as e:
            exception("Could not generate default config, aborting", e, logger=logger)
            exit()
        
        return default_config
    except Exception as e:
        exception(f"Could not load {file}, using default config", e, logger=logger)
        return default_config
    
    return config