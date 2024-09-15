import yaml

class Config:
    def __init__(self, config_file):
        self.config_file = config_file
        self.config = self.load_config()

    def load_config(self):
        with open(self.config_file, 'r') as f:
            return yaml.safe_load(f)

    def get(self, key):
        return self.config[key]

    def set(self, key, value):
        self.config[key] = value

    def save(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, indent=4)

    def __repr__(self) -> str:
        return str(self.config)