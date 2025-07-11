import logging
from typing import Optional, List

from .Auth import Auth
from .Config import APIConfig
from .models.Account import Account
from .models.Hit import Hit
from .models.Profile import Profile
from .models.ProgramType import MovieType, SeriesType
from .utils.parser import parse_profile

# Create a custom logger
logger = logging.getLogger("pydisney")
logger.setLevel(logging.INFO)

# Create a console handler
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)  # Set handler level to DEBUG

# Define a formatter and attach it to the handler
formatter = logging.Formatter("%(levelname)s: %(name)s: %(message)s")
console_handler.setFormatter(formatter)

# Add the handler to the logger
logger.addHandler(console_handler)


class DisneyAPI:
    def __init__(self, email: str, password: str, force_login: bool = False, profile_id: str = None, profile_pin: str = None):

        self._auth = Auth(email=email, password=password, force_login=force_login, profile_id=profile_id, profile_pin=profile_pin)
        self._auth.get_auth_token()

        self.device_id = None
        self.device_platform = None
        self.sessions_id = None

        self.account: Optional[Account] = None
        self._account_init()
        # self._session_init()

        APIConfig.region = "en" if self.account is None else self.account.country
        APIConfig.language = APIConfig.region

    def search(self, query: str) -> List[Hit]:
        res = Auth.make_pagination_request("GET", f"https://disney.api.edge.bamgrid.com/explore/v1.7/search?query={query}")
        for page in res:
            items = page["data"]["page"]["containers"]
            if not items:
                return []
            items = items[0]["items"]

            search_items = []
            for data in items:
                search_items.append(Hit(data))
            return search_items

    def _get_set(self, set_id) -> List[Hit]:
        url = f"https://disney.api.edge.bamgrid.com/explore/v1.7/set/{set_id}"
        res = Auth.make_pagination_request("GET", url)
        hits = []
        for page in res:
            items = page["data"]["set"]["items"]
            hits.extend(Hit.parse_hits(items))
        return hits

    def get_originals(self) -> List[Hit]:
        return self._get_set("3e935bc6-4984-4c49-acd8-a12a2e91ff40")

    def get_movies(self, movie_type: MovieType) -> List[Hit]:
        hits = self._get_set(movie_type.value)
        for hit in hits:
            hit.__is_movie = False
        return hits

    def get_series(self, series_type: SeriesType) -> List[Hit]:
        hits = self._get_set(series_type.value)
        for hit in hits:
            hit.__is_movie = False
        return hits

    def set_download_path(self, path: str) -> None:
        APIConfig.default_path = path

    def get_profiles(self) -> List[Profile]:
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
        res = Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_query)

        profiles = []
        for profile in res["data"]["me"]["account"]["profiles"]:
            profiles.append(parse_profile(profile))
        return profiles

    def get_active_profile(self) -> Profile:
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
        res = Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_query)
        profile = res["data"]["me"]["account"]["activeProfile"]
        return parse_profile(profile)

    def set_active_profile(self, profile_id: str, pin: str = None) -> None:
        access_token, refresh_token = self._auth.set_active_profile(APIConfig.token, profile_id, pin)
        APIConfig.token = access_token
        APIConfig.refresh = refresh_token

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

        res = Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_query)

        acc_json = res["data"]["me"]["account"]
        account_id = acc_json["id"]
        email = acc_json["attributes"]["email"]
        email_verified = acc_json["attributes"]["emailVerified"]
        created_at = acc_json["attributes"]["dssIdentityCreatedAt"]
        try:
            country = acc_json["attributes"]["consentPreferences"]["dataElements"][0]["value"]
        except IndexError:
            # country seems to be missing for newly create accounts
            country = "en"
            logger.warning("Couldn't set country, fallback to default: EN-gb")

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
        res = Auth.make_request("POST", "https://disney.api.edge.bamgrid.com/v1/public/graphql", data=graphql_query)

        sess_json = res["data"]["me"]["activeSession"]
        APIConfig.sessionId = sess_json["sessionId"]
        self.device_id = sess_json["device"]["id"]
        self.device_platform = sess_json["device"]["platform"]

    def get_token(self) -> str:
        return APIConfig.token

    def set_log_level(self, level: int) -> None:
        logger.setLevel(level)
        console_handler.setLevel(level)
