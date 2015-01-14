import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        else:
            return super().default(o)


class Message:
    def __init__(self, name, data):
        self.name = name
        self._data = data

    @property
    def data(self):
        if isinstance(self._data, (bytes, str)):
            self._data = json.loads(self._data)

        return self._data

    @classmethod
    def from_string(cls, string):
        name, data = string.split('|', 1)
        return cls(name, data)

    def __str__(self):
        return self.name + '|' + json.dumps(self.data, cls=DateTimeEncoder)
