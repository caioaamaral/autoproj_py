import yaml

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self) -> dict:
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key: str, fallback=None):
        keys = key.split('.')
        conf: dict = self.config.get(keys.pop(0))

        for key in keys:
            if conf is None:
                return fallback

            conf = conf.get(key, None)

        return conf

    def set(self, key: str, value):
        keys = iter(key.split('.'))

        node = next(keys)
        definition = { node: None }
        current = definition
        while (k := next(keys, None)):
            current[node] = {k: None}
            current = current[node]
            node = k

        current[node] = value
        self.config.update(definition)


    def save(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, indent=4)

    def __repr__(self) -> str:
        return str(self.config)