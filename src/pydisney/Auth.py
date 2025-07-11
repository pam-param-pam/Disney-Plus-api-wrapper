import json
import logging
import re
from datetime import datetime
from json import JSONDecodeError
from typing import List

import requests

from .Config import APIConfig
from .Exceptions import AuthException, ApiException, ProfileException
from .utils.helper import update_file

logger = logging.getLogger("pydisney")
logger = logger.getChild("Auth")


class Auth:
    def __init__(self, email, password, force_login, profile_id, profile_pin):
        self._email = email
        self._force_login = force_login
        self._password = password
        self._profile_id = profile_id
        self._profile_pin = profile_pin

        APIConfig.auth = self

    def _obtain_client_api_key(self):
        """Step 1: Obtain client's api key by parsing html page..."""
        res = APIConfig.session.get("https://www.disneyplus.com")
        pattern = r'"clientId"\s*:\s*"([^"]+)"\s*,\s*"clientApiKey"\s*:\s*"([^"]+)"'
        match = re.search(pattern, res.text)

        if match:
            client_api_key = match.group(2)
            return client_api_key
        else:
            raise AuthException("Unable to obtain client api key. Please open an issue.")

    def _register_device(self, client_api_key):
        """Step 2: Register a device with previously obtained client_api_key"""
        graphql_query = {
            "operationName": "registerDevice",
            "query": "mutation registerDevice($input: RegisterDeviceInput!) { registerDevice(registerDevice: $input) { grant { grantType assertion }, activeSession { partnerName profile { id } } } }",
            "variables": {
                "input": {
                    "deviceFamily": "N/A",
                    "applicationRuntime": "N/A",
                    "deviceProfile": "N/A",
                    "deviceLanguage": "N/A",
                    "devicePlatformId": "N/A",
                    "attributes": {
                        "brand": "N/A",
                        "browserName": "N/A",
                        "browserVersion": "N/A",
                        "manufacturer": "N/A",
                        "operatingSystem": "N/A",
                        "operatingSystemVersion": "N/A",
                    }
                }
            }
        }
        res = APIConfig.session.post("https://disney.api.edge.bamgrid.com/graph/v1/device/graphql", json=graphql_query, headers={"Authorization": f"Bearer {client_api_key}"})
        if not res.ok:
            raise AuthException(res)
        json_data = res.json()
        access_token = json_data["extensions"]["sdk"]["token"]["accessToken"]
        return access_token

    def _login(self, access_token):
        """Step 3. Perform a login with access token obtained during register device"""
        graphql_query = {
            "query": "mutation login($input: LoginInput!) { login(login: $input) { actionGrant account { activeProfile { id } profiles { id attributes { isDefault parentalControls { isPinProtected } } } } activeSession { isSubscriber } identity { personalInfo { dateOfBirth gender } flows { personalInfo { requiresCollection eligibleForCollection } } } } }",
            "variables": {
                "input": {
                    "email": self._email,
                    "password": self._password
                }
            },
            "operationName": "login"
        }

        res = APIConfig.session.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query, headers={"Authorization": f"Bearer {access_token}"})
        if not res.ok:
            raise AuthException(res)
        json_data = res.json()
        profiles = json_data["data"]["login"]["account"]["profiles"]
        access_token = json_data["extensions"]["sdk"]["token"]["accessToken"]
        return access_token, profiles

    def set_active_profile(self, access_token, profile_id, pin=None):
        """Step 4. Set an active profile. Only access token returned here can be used to query data"""
        input_data = {
            "profileId": profile_id
        }

        if pin is not None:
            input_data["entryPin"] = str(pin)

        graphql_mutation = {
            "query": """mutation switchProfile($input: SwitchProfileInput!) { switchProfile(switchProfile: $input) { account { ...account } } } fragment account on Account { id }""",
            "variables": {
                "input": input_data
            },
            "operationName": "switchProfile"
        }
        res = APIConfig.session.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_mutation, headers={"Authorization": f"Bearer {access_token}"})
        # Disney api returns 200 on wrong pin...
        if "Invalid PIN" in res.text:
            raise ProfileException(f"Wrong PIN={pin} for profile ID={profile_id}")

        if "PIN set but not provided" in res.text:
            raise ProfileException(f"profile ID={profile_id} is locked, PIN is required.")

        if not res.ok:
            raise AuthException(res)

        json_data = res.json()
        access_token = json_data["extensions"]["sdk"]["token"]["accessToken"]
        refresh_token = json_data["extensions"]["sdk"]["token"]["refreshToken"]
        return access_token, refresh_token

    def _get_valid_profile(self, profiles):
        # Profile ID to use supplied
        if self._profile_id:
            for profile in profiles:
                if self._profile_id == profile["id"]:
                    is_locked = profile["attributes"]["parentalControls"]["isPinProtected"]
                    if is_locked:
                        if self._profile_pin:
                            return profile["id"], self._profile_pin
                        raise ProfileException(f"Profile '{self._profile_id}' is locked but no PIN was provided.")
                    else:
                        return profile["id"], None
            raise ProfileException(f"Profile with ID={self._profile_id} not found.")

        # No profile ID was provided, try to use default profile
        for profile in profiles:
            if profile["attributes"]["isDefault"]:
                is_locked = profile["attributes"]["parentalControls"]["isPinProtected"]
                if is_locked:
                    if self._profile_pin:
                        logger.warning("Default profile is locked! Using supplied PIN.")
                        return profile["id"], self._profile_pin
                    logger.info("Default profile is locked and no PIN provided. Will search for an unlocked profile.")
                    break

        # Try to find any other unlocked profile
        for profile in profiles:
            is_locked = profile["attributes"]["parentalControls"]["isPinProtected"]
            if not is_locked:
                return profile["id"], None

        # If default was locked and no other profiles are available
        raise ProfileException("No unlocked profiles available. All profiles are locked and no PIN was provided.")

    def _get_auth_token_tru_api(self):
        logger.info("Loging using disney's api")
        logger.warning("Loging using Disney's api repeatedly will cause account blocks")
        client_api_key = self._obtain_client_api_key()
        device_access_token = self._register_device(client_api_key)
        non_profile_access_token, profiles = self._login(device_access_token)

        profile_id, profile_pin = self._get_valid_profile(profiles)
        access_token, refresh_token = self.set_active_profile(non_profile_access_token, profile_id, profile_pin)
        APIConfig.token = access_token
        APIConfig.refresh = refresh_token
        update_file()

    @staticmethod
    def refreshToken():
        with open("token.json", "r", encoding="utf8") as file:
            data = json.load(file)

            refresh = data["refresh"]

            logger.info("Refreshing access token using refresh token from token.json file")
            graph_mutation = {
                "query": "mutation refreshToken($input:RefreshTokenInput!){refreshToken(refreshToken:$input){activeSession{sessionId}}}",
                "variables": {
                    "input": {
                        "refreshToken": refresh
                    }
                },
                "operationName": "refreshToken"
            }

            res = APIConfig.session.post(url="https://disney.api.edge.bamgrid.com/graph/v1/device/graphql",
                                         json=graph_mutation,
                                         headers={"authorization": APIConfig.auth._obtain_client_api_key()})
            if not res.ok:
                raise AuthException(res)

            if not res.json()["data"]:
                errors = []
                for error in res.json()["errors"]:
                    errors.append(error)
                logger.info("Couldn't refresh access token with refresh token:\n%s", errors)
                #  trying one last time to get access token via standard login procedure using email and password
                APIConfig.auth._get_auth_token_tru_api()
                return

            res_json = res.json()

            APIConfig.token = res_json["extensions"]["sdk"]["token"]["accessToken"]
            APIConfig.refresh = res_json["extensions"]["sdk"]["token"]["refreshToken"]
            update_file()

    @staticmethod
    def make_request(method: str, url: str, data: dict = None, headers: dict = None, params: dict = None, files: dict = None) -> dict:
        default_headers = {
            'accept': 'application/vnd.media-service+json; version=6',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            'x-bamsdk-platform': "macOS",
            'x-bamsdk-version': '23.1',
            'x-dss-edge-accept': 'vnd.dss.edge+json; version=2',
            'x-dss-feature-filtering': 'true',
            'Origin': 'https://www.disneyplus.com',
            'authorization': APIConfig.token
        }

        if params is None:
            params = {}

        if headers is None:
            headers = {}

        logger.debug(f"Calling... Url={url}, Method={method}, Headers={headers}")

        headers.update(default_headers)
        response = requests.request(method, url, headers=headers, json=data, params=params, files=files, timeout=10)

        if not response.ok:
            raise ApiException(response)

        return response.json()

    @staticmethod
    def make_pagination_request(method: str, url: str, data: dict = None, headers: dict = None, params: dict = None, files: dict = None) -> List[dict]:
        if params is None:
            params = {}
        params.setdefault('limit', 200)
        params.setdefault('offset', 0)

        aggregated_results = []
        current_offset = params['offset']
        limit = params['limit']

        while True:
            logger.debug(f"Fetching page with offset={current_offset}, limit={limit}")
            params['offset'] = current_offset

            # Use the existing make_request method
            response_json = Auth.make_request(
                method=method,
                url=url,
                data=data,
                headers=headers,
                params=params,
                files=files
            )

            from .utils.parser import find_pagination_values  # circular import
            pagination_values = find_pagination_values(response_json)

            logger.debug(f"Pagination Values: {pagination_values}")

            aggregated_results.append(response_json)

            # Check if there are more pages
            if pagination_values and pagination_values.get('hasMore', False):
                current_offset += limit
            else:
                break

        return aggregated_results

    @staticmethod
    def make_stream_request(url):
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}

        res = APIConfig.session.get(url=url, headers=headers, stream=True, timeout=10)
        if res.status_code == 401:
            raise AuthException(res)
        if not res.ok:
            raise ApiException(res)

        return res

    def get_auth_token(self):
        if self._force_login:
            self._get_auth_token_tru_api()
            return
        try:
            with open("token.json", "r", encoding="utf8") as file:

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
                    logger.info("Access token is expired, refreshing...")

                    self.refreshToken()

        except (FileNotFoundError, KeyError, JSONDecodeError):

            logger.info("Creating token.json file")
            open("token.json", "a+", encoding="utf8").close()

            self._get_auth_token_tru_api()
