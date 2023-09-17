import logging

import requests

from Config import APIConfig
from Exceptions import ApiException
from Login import Login
from models.Account import Account
from models.Language import Language
from models.Movie import Movie
from models.Rating import Rating
from models.Series import Series
from utils.parser import parse_hits, parse_profile

logging.basicConfig()

logger = logging.getLogger('DisneyAPI')
logger.setLevel(logging.DEBUG)


class DisneyAPI:
    def __init__(self, email, password, proxies=False, force_login=False):

        Login(email=email, password=password, proxies=proxies, force_login=force_login).get_auth_token()

        self.device_id = None
        self.device_platform = None
        self.sessions_id = None

        self.account: Account = None
        self.account_init()
        self.session_init()
        APIConfig.region = "en" if self.account is None else self.account.country
        APIConfig.language = APIConfig.region

    def search(self, query, rating: Rating = Rating.ADULT):

        res = requests.get(
            f"https://disney.content.edge.bamgrid.com/svc/search/disney/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/{rating.value}/language/{APIConfig.language}/queryType/ge/pageSize/0/query/{query}",
            headers={"authorization": "Bearer " + APIConfig.token}, timeout=10)
        if res.status_code != 200:
            raise ApiException(res)
        return parse_hits(res.json()["data"]["search"]["hits"], True)

    def search_movies(self, query, rating: Rating = Rating.ADULT):

        return [item for item in self.search(query, rating) if isinstance(item, Movie)]

    def search_series(self, query, rating: Rating = Rating.ADULT):

        return [item for item in self.search(query, rating) if isinstance(item, Series)]

    def set_language(self, language: Language):
        APIConfig.language = language.value

    def set_download_path(self, path):
        APIConfig.default_path = path

    def get_profiles(self):
        graphql_query = {
            "query": """
                query {
                    me {
                        account {
                            profiles {
                                ...profile
                            }
                        }
                    }
                }
                fragment profile on Profile {
                    id
                    name
                    attributes {
                        avatar {
                            id
                            userSelected
                        }
                        isDefault
                        kidsModeEnabled
                        languagePreferences {
                            appLanguage
                            playbackLanguage
                            subtitleLanguage
                            subtitlesEnabled
                        }
                    }

                }
            """,
            "variables": {}
        }
        res = APIConfig.session.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query,
                                     headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        profiles = []
        for profile in res.json()["data"]["me"]["account"]["profiles"]:
            profiles.append(parse_profile(profile))
        return profiles

    def get_active_profile(self):
        graphql_query = {
            "query": """
                query {
                    me {
                        account {
                            activeProfile {
                                ...profile
                            }
                        }
                    }
                }
                fragment profile on Profile {
                    id
                    name

                    attributes {
                        avatar {
                            id
                            userSelected
                        }
                        isDefault
                        kidsModeEnabled
                        languagePreferences {
                            playbackLanguage
                            subtitleLanguage
                            subtitlesEnabled
                            appLanguage
                        }
                    }

                }
            """,
            "variables": {}
        }
        res = APIConfig.session.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query,
                                     headers={"authorization": "Bearer " + APIConfig.token}, timeout=10)
        if res.status_code != 200:
            raise ApiException(res)
        profile = res.json()["data"]["me"]["account"]["activeProfile"]
        return parse_profile(profile)

    def set_active_profile(self, profile_id):
        graphql_mutation = {
            "query": """
                mutation switchProfile($input: SwitchProfileInput!) {
                    switchProfile(switchProfile: $input) {
                        account {
                            ...account
                        }
                    }
                }
                fragment account on Account {
                    id
                }
            """,
            "variables": {
                "input": {
                    "profileId": profile_id
                }
            },
            "operationName": "switchProfile"
        }
        res = requests.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_mutation,
                            headers={"authorization": "Bearer " + APIConfig.token}, timeout=10)
        if res.status_code != 200:
            raise ApiException(res)
        APIConfig.token = res.json()["extensions"]["sdk"]["token"]["accessToken"]

    def session_init(self):
        graphql_query = {
            "query": """
                        query {
                            me {
                                activeSession {
                                    ...session
                                }
                            }
                        }
                        fragment session on Session {
                             device {
                                id
                             platform
                             }
                            sessionId
                        }
                    """,
            "variables": {}
        }
        res = requests.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query,
                            headers={"authorization": "Bearer " + APIConfig.token}, timeout=10)
        if res.status_code != 200:
            raise ApiException(res)
        sess_json = res.json()["data"]["me"]["activeSession"]
        APIConfig.sessionId = sess_json["sessionId"]
        self.device_id = sess_json["device"]["id"]
        self.device_platform = sess_json["device"]["platform"]

    def get_token(self):
        return APIConfig.token

    def account_init(self):
        graphql_query = {
            "query": """
                query {
                    me {
                        account {
                            ...account
                        }
                    }
                }
                fragment account on Account {
                    id
                    attributes {
                        consentPreferences {
                            dataElements {
                                name
                                value
                            }
                        }
                        dssIdentityCreatedAt
                        email
                        emailVerified
                        userVerified
                    }
                }
            """,
            "variables": {}
        }
        res = requests.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query,
                            headers={"authorization": "Bearer " + APIConfig.token}, timeout=10)
        if res.status_code != 200:
            raise ApiException(res)
        acc_json = res.json()["data"]["me"]["account"]
        account_id = acc_json["id"]
        email = acc_json["attributes"]["email"]
        email_verified = acc_json["attributes"]["emailVerified"]
        created_at = acc_json["attributes"]["dssIdentityCreatedAt"]
        try:
            country = acc_json["attributes"]["consentPreferences"]["dataElements"][0]["value"]
        except IndexError:
            # country seems to be missing for newly create accounts
            country = "en"
            logger.warning("Couldn't set country, fallbacking to default: EN-gb")

        account = Account(account_id=account_id, email=email, created_at=created_at, country=country, is_email_verified=email_verified)
        self.account = account
