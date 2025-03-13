import datetime
import json


class DateTimeEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, (datetime.datetime, datetime.date)):
            return o.isoformat()
        else:
            try:
                return super().default(o)
            except TypeError as exc:
                raise TypeError("{} is not JSON serializable.".format(type(o))) from exc


class Message:
    # TODO: Could be optimized to not decode JSON until needed.
    # TODO: Could be optimized to not encode JSON until needed.
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @classmethod
    def from_string(cls, string):
        name, json_data = string.split("|", 1)

        return cls(name, json.loads(json_data))

    def __str__(self):
        return self.name + "|" + json.dumps(self.data, cls=DateTimeEncoder)
