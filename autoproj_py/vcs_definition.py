from dataclasses import dataclass, field
from typing import ClassVar


class VCSHandler:

    TOKEN = None

    def parse(self, data: dict) -> 'VCSDefinition':
        raise NotImplementedError


class GithubHandler(VCSHandler):

    TOKEN = 'github'

    @classmethod
    def parse(cls, data: dict):
        _value = data[cls.TOKEN]
        _type = 'git'
        _url =  f'git@github.com:{_value}.git'
        _options = {}
        return VCSDefinition(_type, _url, _options)
    

@dataclass
class VCSDefinition:

    HANDLERS: ClassVar[list[VCSHandler]] = [GithubHandler]

    type: str
    url: str
    options: dict = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: dict):
        for handler in cls.HANDLERS:
            if handler.TOKEN in data:
                return handler.parse(data)

        return cls(
            data['type'],
            data['url'],
            data.get('options', {})
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
