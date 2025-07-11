from typing import Union

from requests import Response

class PyDisneyException(Exception):
    """Default exception class for all pydisney exceptions"""
    pass

class ProfileException(PyDisneyException):
    """Raised when there is a problem with setting a default profile"""
    pass

class AuthException(PyDisneyException):
    def __init__(self, message: Union[Response, str]):
        if isinstance(message, Response):
            self.message = f"{message.text}\n{message.status_code}"
        else:
            self.message = message
        super().__init__()

class ApiException(PyDisneyException):
    def __init__(self, response: Response):
        self.message = response
        super().__init__(f"{self.message.text}\n{self.message.status_code}")

class GraphqlException(PyDisneyException):
    def __init__(self, response: list):
        self.message = response
        super().__init__(str(response))

class FFmpegException(PyDisneyException):
    def __init__(self):
        super().__init__("Unknown ffmpeg error occurred")
