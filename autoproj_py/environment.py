class Environment:

    def __init__(self, file):
        self.file = file
        self._envars = dict()
        self._source_after = list()

    def __repr__(self):
        return f'Environment(envars:{self._envars}, source_after:{self._source_after})'

    def set(self, key: str, value: str|int|float):
        self._envars[key] = value

    def remove(self, key: str):
        self._envars.pop(key, None)

    def source_after(self, file: str):
        self._source_after.append(file)

    def save(self):
        with open(self.file, 'w') as f:
            for key, value in self._envars.items():
                f.write(f'export {key}={value}\n')
            for file in self._source_after:
                f.write(f'. {file}\n')
