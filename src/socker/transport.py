import json


class SockMessage:
    def __init__(self, name, data):
        self.name = name
        self.data = data

    @classmethod
    def from_redis(cls, reply):
        return cls(reply.channel, json.loads(reply.value))

    @classmethod
    def from_string(cls, string):
        name, json_str = string.split('|', 1)
        data = json.loads(json_str)

        return cls(name, data)

    def __str__(self):
        return self.name + '|' + json.dumps(self.data)