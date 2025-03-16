from dataclasses import dataclass
from typing import ClassVar


class VCSHandler:

    TOKEN = None

    def parse(self, data: dict) -> 'VCSDefinition':
        raise NotImplementedError


class GithubHandler(VCSHandler):

    @classmethod
    def parse(cls, data: dict):
        _value = data[cls.token]
        _type = 'git'
        _url =  f'git@github.com:{_value}.git'
        _options = {}
        return VCSDefinition(_type, _url, _options)
    

@dataclass
class VCSDefinition:

    HANDLERS: ClassVar[list[VCSHandler]] = []

    type: str
    url: str
    options: dict

    @classmethod
    def from_dict(cls, data):
        for handler in cls.HANDLERS:
            if handler.TOKEN in data:
                return handler.parse(data)

        return cls(
            data['type'],
            data['url'],
            data['options']
        )

    @classmethod
    def from_url(cls, url: str):
        if url.startswith('git'):
            return cls('git', url, {})
        if url.startswith('https'):
            return cls('https', url, {})
        if url.startswith('file'):
            return cls('file', url, {})

    def __str__(self):
        return f'VCSDefinition(type={self.type}, url={self.url}, options={self.options})'

    def __repr__(self):
        return str(self)
