import logging
from typing import Union, Dict


from Auth import Auth
from Config import APIConfig
from models.Account import Account
from models.Language import Language
from models.Movie import Movie
from models.ProgramType import MovieType, SeriesType
from models.Rating import Rating
from models.Series import Series
from utils.parser import parse_hits, parse_profile

logging.basicConfig()

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)


class DisneyAPI:
    def __init__(self, email: str, password: str, proxies: Dict = False, force_login: bool = False):

        auth = Auth(email=email, password=password, proxies=proxies, force_login=force_login)
        auth.get_auth_token()

        self.device_id = None
        self.device_platform = None
        self.sessions_id = None

        self.account: Account = None
        self._account_init()
        self._session_init()

        APIConfig.region = "en" if self.account is None else self.account.country
        APIConfig.language = APIConfig.region

    def search(self, query: str, rating: Rating = Rating.ADULT):
        res = Auth.make_get_request(
            f"https://disney.content.edge.bamgrid.com/svc/search/disney/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/{rating.value}/language/{APIConfig.language}/queryType/ge/pageSize/45/query/{query}")
        return parse_hits(res.json()["data"]["search"]["hits"], True)

    def search_movies(self, query: str, rating: Rating = Rating.ADULT):

        return [item for item in self.search(query, rating) if isinstance(item, Movie)]

    def search_series(self, query: str, rating: Rating = Rating.ADULT):

        return [item for item in self.search(query, rating) if isinstance(item, Series)]

    def set_language(self, language: Language):
        APIConfig.language = language.value

    def set_download_path(self, path: str):
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
        res = Auth.make_post_request("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query)

        profiles = []
        for profile in res.json()["data"]["me"]["account"]["profiles"]:
            profiles.append(parse_profile(profile))
        return profiles

    def get_active_profile(self):
        """https://global.edge.bamgrid.com/accounts/me/active-profile
        possible duplicate"""

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
        res = Auth.make_post_request("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query)
        profile = res.json()["data"]["me"]["account"]["activeProfile"]
        return parse_profile(profile)

    def search_program_type(self, program_type: Union[MovieType, SeriesType], rating: Rating = Rating.ADULT):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/GenericSet/version/6.0/region/{APIConfig.region}/audience/k-false,l-true/maturity/{rating.value}/language/{APIConfig.language}/setId/{program_type.value}/pageSize/100000/page/1")
        return parse_hits(res.json()["data"]["GenericSet"]["items"])

    def set_active_profile(self, profile_id: str, pin: str = None):
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
                    "profileId": profile_id,
                    "entryPin": pin

                }
            },
            "operationName": "switchProfile"
        }
        res = Auth.make_post_request("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_mutation)

        APIConfig.token = res.json()["extensions"]["sdk"]["token"]["accessToken"]

    def _account_init(self):
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

        res = Auth.make_post_request("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query)

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

        account = Account(account_id=account_id, email=email, created_at=created_at, country=country,
                          is_email_verified=email_verified)
        self.account = account

    def _session_init(self):
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
        res = Auth.make_post_request("https://disney.api.edge.bamgrid.com/v1/public/graphql", json=graphql_query)

        sess_json = res.json()["data"]["me"]["activeSession"]
        APIConfig.sessionId = sess_json["sessionId"]
        self.device_id = sess_json["device"]["id"]
        self.device_platform = sess_json["device"]["platform"]

    def get_token(self):
        return APIConfig.token
