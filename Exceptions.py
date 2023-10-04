import requests


class AuthException(Exception):
    def __init__(self, message: requests.Response):
        self.message = message
        super().__init__(f"{self.message.text}\n{self.message.status_code}")

class ApiException(Exception):
    def __init__(self, response: requests.Response):
        self.message = response
        super().__init__(f"{self.message.text}\n{self.message.status_code}")
