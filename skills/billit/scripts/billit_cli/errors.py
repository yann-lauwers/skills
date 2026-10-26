DONE = 0
FAILED = 1
USAGE = 2
NOT_FOUND = 3
AUTH = 4
DISAGREES = 5
REFUSED = 6
PRECONDITION = 7


class Fail(Exception):
    def __init__(self, code, message):
        super().__init__(message)
        self.code = code
        self.message = message


class WriteRefused(Fail):
    def __init__(self, status, message):
        super().__init__(REFUSED, message)
        self.status = status
