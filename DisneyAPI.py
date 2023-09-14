import json
import logging

import requests

from Config import APIConfig
from Exceptions import ApiException
from Login import Login
from models.Account import Account
from models.Language import Language
from models.Rating import Rating
from utils.parser import parseHits, parseProfile

logging.basicConfig()

logger = logging.getLogger('DisneyAPI')
logger.setLevel(logging.DEBUG)


class DisneyAPI(object):
    def __init__(self, email, password, proxies=False, forceLogin=False):

        Login(email=email, password=password, proxies=proxies, forceLogin=forceLogin).getAuthToken()

        self.deviceId = None
        self.devicePlatform = None
        self.sessionsId = None

        self.account: Account = None
        self.AccountInit()
        self.SessionInit()
        APIConfig.region = "en" if self.account is None else self.account.country
        APIConfig.language = APIConfig.region

    def search(self, query, rating: Rating = Rating.Adult):

        res = requests.get(
            f"https://disney.content.edge.bamgrid.com/svc/search/disney/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/{rating.value}/language/{APIConfig.language}/queryType/ge/pageSize/0/query/{query}",
            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        return parseHits(res.json()["data"]["search"]["hits"], True)


    def setLanguage(self, language: Language):
        APIConfig.language = language.value

    def getProfiles(self):
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
            profiles.append(parseProfile(profile))
        return profiles

    def getActiveProfile(self):
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
                                     headers={"authorization": "Bearer " + APIConfig.token})
        print(res.text)
        if res.status_code != 200:
            raise ApiException(res)
        profile = res.json()["data"]["me"]["account"]["activeProfile"]
        return parseProfile(profile)


    def setActiveProfile(self, profileId):
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
                    "profileId": profileId
                }
            },
            "operationName": "switchProfile"
        }
        res = requests.post("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_mutation,
                            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        APIConfig.token = res.json()["extensions"]["sdk"]["token"]["accessToken"]

    def SessionInit(self):
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
                            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        sess_json = res.json()["data"]["me"]["activeSession"]
        APIConfig.sessionId = sess_json["sessionId"]
        self.deviceId = sess_json["device"]["id"]
        self.devicePlatform = sess_json["device"]["platform"]

    def AccountInit(self):
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
                            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        acc_json = res.json()["data"]["me"]["account"]
        id = acc_json["id"]
        email = acc_json["attributes"]["email"]
        emailVerified = acc_json["attributes"]["emailVerified"]
        createdAt = acc_json["attributes"]["dssIdentityCreatedAt"]
        try:
            country = acc_json["attributes"]["consentPreferences"]["dataElements"][0]["value"]
        except IndexError:
            country = "en"
            logger.warning("Couldn't set country, fallbacking to default: EN-gb")

        account = Account(id=id, email=email, createdAt=createdAt, country=country, isEmailVerified=emailVerified)
        self.account = account


