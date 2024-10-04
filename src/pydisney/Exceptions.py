from requests import Response


class AuthException(Exception):
    def __init__(self, message: Response):
        self.message = message
        super().__init__(f"{self.message.text}\n{self.message.status_code}")

class ApiException(Exception):
    def __init__(self, response: Response):
        self.message = response
        super().__init__(f"{self.message.text}\n{self.message.status_code}")

class GraphqlException(Exception):
    def __init__(self, response: list):
        self.message = response
        super().__init__(str(response))

class FFmpegException(Exception):
    def __init__(self):
        super().__init__("Unknown ffmpeg error occured")
