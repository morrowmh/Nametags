DEFAULT_BOT_CONFIG_FILENAME = "config.toml"
DEFAULT_BOT_CONFIG = {
    "bot": {
        "name": "Nametags Discord Bot",
        "version": "1.0.0"
    },

    "logging": {
        "base_level": "INFO",
        "file": "logs/bot.log",
        "rotate_daily": True,
        "backup_count": 50,
        "disable_file_logging": False,
        "disable_console_logging": False
    }
}