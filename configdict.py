class configdict(dict):
    def __init__(self, default_config, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_config = default_config
    
    def __missing__(self, key):
        if key not in self.default_config:
            raise KeyError(key)
        ret = self[key] = self.default_config[key]
        return ret