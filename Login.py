import json
import logging
import re
from datetime import datetime, timedelta
from json import JSONDecodeError

import requests

from Config import APIConfig
from Exceptions import LoginException

logger = logging.getLogger('Login')
logger.setLevel(logging.DEBUG)


class Login(object):
    def __init__(self, email, password, proxies=False):
        self._email = email
        self._password = password
        self._web_page = 'https://www.disneyplus.com/login'
        self._devices_url = "https://disney.api.edge.bamgrid.com/devices"
        self._login_url = 'https://disney.api.edge.bamgrid.com/idp/login'
        self._token_url = "https://disney.api.edge.bamgrid.com/token"
        self._grant_url = 'https://disney.api.edge.bamgrid.com/accounts/grant'
        self._session = requests.Session()

        if proxies:
            self._session.proxies.update(proxies)

    def _clientApiKey(self):
        res = self._session.get(self._web_page)
        match = re.search("window.server_path = ({.*});", res.text)
        janson = json.loads(match.group(1))
        clientapikey = janson["sdk"]["clientApiKey"]
        return clientapikey

    def _assertion(self, client_apikey):

        postdata = {
            "applicationRuntime": "firefox",
            "attributes": {},
            "deviceFamily": "browser",
            "deviceProfile": "macosx"
        }

        header = {"authorization": f"Bearer {client_apikey}", "Origin": "https://www.disneyplus.com"}
        res = self._session.post(url=self._devices_url, headers=header, json=postdata)

        assertion = res.json()["assertion"]

        return assertion

    def _access_token(self, client_apikey, assertion):

        header = {"authorization": "Bearer {}".format(client_apikey), "Origin": "https://www.disneyplus.com"}

        postdata = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "latitude": "0",
            "longitude": "0",
            "platform": "browser",
            "subject_token": assertion,
            "subject_token_type": "urn:bamtech:params:oauth:token-type:device"
        }

        res = self._session.post(url=self._token_url, headers=header, data=postdata)

        if res.status_code != 200:
            raise LoginException(res)

        access_token = res.json()["access_token"]
        return access_token

    def _login(self, access_token):
        headers = {
            'accept': 'application/json; charset=utf-8',
            'authorization': "Bearer {}".format(access_token),
            'content-type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.disneyplus.com',
            'Referer': 'https://www.disneyplus.com/login/password',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'x-bamsdk-platform': 'windows',
            'x-bamsdk-version': '3.10',
        }

        data = {'email': self._email, 'password': self._password}
        res = self._session.post(url=self._login_url, data=json.dumps(data), headers=headers)
        if res.status_code != 200:
            raise LoginException(res)
        id_token = res.json()["id_token"]
        return id_token

    def _grant(self, id_token, access_token):

        headers = {
            'accept': 'application/json; charset=utf-8',
            'authorization': f"Bearer {access_token}",
            'content-type': 'application/json; charset=UTF-8',
            'Origin': 'https://www.disneyplus.com',
            'Referer': 'https://www.disneyplus.com/login/password',
            'Sec-Fetch-Mode': 'cors',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/76.0.3809.132 Safari/537.36',
            'x-bamsdk-platform': 'windows',
            'x-bamsdk-version': '3.10',
        }

        data = {'id_token': id_token}

        res = self._session.post(url=self._grant_url, data=json.dumps(data), headers=headers)
        assertion = res.json()["assertion"]

        return assertion

    def _finalToken(self, subject_token, client_apikey):

        header = {"authorization": f"Bearer {client_apikey}", "Origin": "https://www.disneyplus.com"}

        postdata = {
            "grant_type": "urn:ietf:params:oauth:grant-type:token-exchange",
            "latitude": "0",
            "longitude": "0",
            "platform": "browser",
            "subject_token": subject_token,
            "subject_token_type": "urn:bamtech:params:oauth:token-type:account"
        }

        res = self._session.post(url=self._token_url, headers=header, data=postdata)

        if res.status_code != 200:
            raise LoginException(res)
        access_token = res.json()["access_token"]
        expires_in = res.json()["expires_in"]
        refresh_token = res.json()["refresh_token"]

        return access_token, expires_in, refresh_token

    def _updateFile(self):
        with open("token.json", "w") as file:
            current_time = datetime.now()
            expiration_time = current_time + timedelta(hours=4)
            token_data = {
                "token": APIConfig.token,
                "refresh": APIConfig.refresh,
                "expiration_time": expiration_time.strftime("%Y-%m-%d %H:%M:%S")
            }
            json.dump(token_data, file)

    def _getAuthTokenTruApi(self):
        logger.info("Loging using disney's api")
        logger.warning("Loging using Disney's api repeatedly will cause account blocks")
        clientapikey_ = self._clientApiKey()
        assertion_ = self._assertion(clientapikey_)

        access_token_ = self._access_token(clientapikey_, assertion_)
        id_token_ = self._login(access_token_)

        user_assertion = self._grant(id_token_, access_token_)
        TOKEN, EXPIRE, REFRESH = self._finalToken(user_assertion, clientapikey_)

        APIConfig.token = TOKEN
        APIConfig.refresh = REFRESH
        self._updateFile()

    def getAuthToken(self):
        APIConfig.session = self._session
        try:
            with open("token.json", "r") as file:

                data = json.load(file)
                token = data["token"]
                refresh = data["refresh"]
                expiration_time_str = data["expiration_time"]

                # Convert the expiration time string back to a datetime object
                expiration_time = datetime.strptime(expiration_time_str, "%Y-%m-%d %H:%M:%S")

                # Check if the token is still valid
                current_time = datetime.now()
                if current_time < expiration_time:
                    logger.info("Authenticating using token from token.json file")

                    APIConfig.token = token
                    APIConfig.refresh = refresh
                else:
                    logger.info("Loging using refresh token from token.json file")
                    graph_mutation = {
                        "query": "mutation refreshToken($input:RefreshTokenInput!){refreshToken(refreshToken:$input){activeSession{sessionId}}}",
                        "variables": {
                            "input": {
                                "refreshToken": refresh
                            }
                        },
                        "operationName": "refreshToken"
                    }
                    res = self._session.post(url="https://disney.api.edge.bamgrid.com/graph/v1/device/graphql",
                                             json=graph_mutation, headers={"authorization": self._clientApiKey()})
                    if res.status_code != 200:
                        raise LoginException(res)

                    res_json = res.json()
                    APIConfig.token = res_json["extensions"]["sdk"]["token"]["accessToken"]
                    APIConfig.refresh = res_json["extensions"]["sdk"]["token"]["refreshToken"]
                    self._updateFile()

        except (FileNotFoundError, KeyError, JSONDecodeError) as e:

            logger.info("Creating token.json file")
            open("token.json", "a+").close()

            self._getAuthTokenTruApi()
