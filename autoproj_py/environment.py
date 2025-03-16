class Environment:

    def __init__(self, file):
        self.file = file
        self.envars = dict()

    def set(self, key, value):
        self.envars[key] = value

    def unset(self, key):
        self.envars.pop(key, None)

    def save(self):
        with open(self.file, 'w') as f:
            for key, value in self.envars.items():
                f.write(f'export {key}={value}\n')
