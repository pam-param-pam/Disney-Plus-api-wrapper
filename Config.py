import threading

import requests


class APIConfig(object):
    region = None
    language = None
    session: requests.Session = None
    token = None
    refresh = None
    token_expire = None
    sessionId = None
    _instance = None
    _lock = threading.Lock()
    default_path = "download"

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                # Another thread could have created the instance
                # before we acquired the lock. So check that the
                # instance is still nonexistent.
                if not cls._instance:
                    cls._instance = super().__new__(cls)
        return cls._instance
