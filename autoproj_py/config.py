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
        """Set a value in the configuration.

        Args:
            key: The configuration key to set
            value: The value to set
        """
        keys = key.split('.')
        current = self.config

        # Traverse the config dictionary to the second-to-last key
        for key in keys[:-1]:
            if key not in current:
                current[key] = {}
            current = current[key]

        # Set the value at the last key
        current[keys[-1]] = value

    def ask(self, key: str, question: str, default=None):
        """Ask the user a question and store the answer in the configuration.

        Args:
            key: The configuration key to store the answer under
            question: The question to ask the user
            default: Default value if user provides no input
        """
        current_value = self.get(key)
        if current_value is not None:
            return current_value

        if default is not None:
            question = f"{question} [{default}]: "
        else:
            question = f"{question}: "

        answer = input(question).strip()
        if not answer and default is not None:
            answer = default

        self.set(key, answer)
        self.save()
        return answer

    def save(self):
        with open(self.config_file, 'w') as f:
            yaml.dump(self.config, f, indent=4)

    def __repr__(self) -> str:
        return str(self.config)