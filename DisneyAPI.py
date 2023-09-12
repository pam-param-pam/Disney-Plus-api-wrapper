import logging

import requests

from Config import APIConfig
from Exceptions import ApiException
from Login import Login
from Models import Account, Rating, HitType, Movie, Series, Profile, Language

logging.basicConfig()

logger = logging.getLogger('DisneyAPI')
logger.setLevel(logging.DEBUG)


class DisneyAPI(object):
    def __init__(self, email, password, proxies):

        Login(email=email, password=password, proxies=proxies).getAuthToken()

        # APIConfig.session = requests.Session()
        # APIConfig.token = "eyJ6aXAiOiJERUYiLCJraWQiOiJ0Vy10M2ZQUTJEN2Q0YlBWTU1rSkd4dkJlZ0ZXQkdXek5KcFFtOGRJMWYwIiwiY3R5IjoiSldUIiwiZW5jIjoiQzIwUCIsImFsZyI6ImRpciJ9..YieGK5pctPTbDnoK.CAgmBZ6SWENwN4KV0KAaiK_ycvU6GLJnug97CDHkJ54mrx26YTo4KDdeca-7uSSAuLzqmF6F-Z_czdQbk_0r730UG3OF9QYQhf7sirb1-FOtMHEmCvuiLll1H1EPPdR13YmcudWmCIzcmsLqpXGgACpMn6goL8fHAfbSmZINdKw3c1KRi5nFU3sqVGSSlSLAhJNOXDYdNHzWremsOdr1wtFl-JKw5GWqbB6ptdWPXPg4ymdlbcomWbSOpXDGYfh-JY1obDiGQ0F6epz7Riyjg2R4YiZvczm3Cp3aewtpGvrNnOprPkfBvFjUdvTGhLCqOP4xS2OVfy06OuX5st59Kj6kq-ZVxtWhs7kgeluMGRn4CjJ_CqKmDTBsTZfYcuxymgQ6Eqw6K9Gv7H6TI8MWRQ9R2OrkDoCBtwS8TLVoKgtuHpkyEhBEoB6wCJQ546BeAgziZDUK9Z4KOODVVI3l63gqgc3MDti1HRUZ3IZKVwkdozUu05BAvBqUXFopv6cxiU-kQLLNrskxuUzLrg178ePQTvoBobSC2ZFig88TBDjA-cNQyeuKdOqwWqfPmBrMdjYRzGH87HipUgkTiCdn-g3fP5xj2sMQPRYAqwKdm_0MfEtXl8yMlAh3K00wDHqP6wD1bQSKlGJJ3jb78QZXH2bnz6XejuBJJU2NnIdTTTwEA9wF2MafLYhb7xlS621Prr2G1K7lmtMc-kNPDbXU-G3xRoEx8WGRKRbuB0QlFcy6two_PtX7CDcmP4LRyTqsR-Kz4aQXwcXFyQAuwL5-8Va2nswdOHNcyH66M00bD5j97ZBLB1uWAI6R6kbJK8zTBcVm9Hef3MkcdawuoK6b-gTjhRCMl3TbrOo02xmHCtASHmwW86uGJBmv8flRK0mNvnwTtMHb3G1qVrlpZHDMJUhbNCfd08rxZ_Yg6_0c27-UH-zXBL9RXeO4ZiG0BoSah9ZocXF-zbwzf7qFgSyBfd9LhxjBvB5R_YOgGLjRYsRXcQeEdvgiCWt2RILAl8x1gVpoBg_pyaAGxdP7ACp2Guk0_fdF34Yxg040qp_XfiEfHcHzxw5qxCYl-2CYQS-h_gPnJbz2nPsVYCY2qILT-qEzv4zMPMrWtmirwez1Cn8TCMWpIS7iCv9qSAusBgiec6ZaFdggrzOmwmniYSQ_OdevfmlZHQuUZnn8QkoVh2cv7xM0y3dx1383fTGNKDDbTvz85T2zEM5rx3qpD_UmhHJ1kX34rx-4yFITGldJP4siGK-GInmcehS5me94-es4vp-0MEkHn70Wbd0DEyJNc-wOXz5s-fGAvUJa6T8J69PJ0SC903h-qgxctC7uMaEiGIghBRirLBKJnQxOTQb_7i3DikV9DU4AzKAFeK07x6K0ble2EZ-hYK9TTnEjfTqJlvBIkXpPb2y0oeDJIX_cSMP9qR6ujI18Egmkq1LNee4tIJn_FOAChdnVP2o66_pOjThUlgJVlF6Zs0Aca5R76x9A7LWnSPPMBbbi5pY_kGrEp5pMI-wizyFHaxRmX0P-Xhhwq6XkiflDBnZGHXHSBMQCs3UlZROeucN5Z7tXDWjSWQv-Z1lChhtHMasMAbXUJIbomNQYRgzLu4BzCy6_SZGqMP8eQFnRQonuJ1bB7Q4yDnmlZvfWmys_eQK4i3jRBGgoVJOsjXgliT7ChjRHdAdJPQjZcJKdypjinDS-PgCeyO3AOJFDgu45scW8Jv1ZuNhgT5E4pB7zFkglrbeB8uCwR74kMcOl2zLZVA3GcswhwlBkAzKekpDk9n-PP1glaDsUTMogWWsPki9SMzRnCGCzTEgOy_jDVqe4P0THUWr48_M23xGqXph5Xh5F2SEjQUI1EGuT3-ggQV2RsG5QTunWbiycgl6F266i9Wrtay6Afj2PHMCWCR1u9ZHZN5Vq84QAUXELIg5GKPOfWczI-_ny0a92dOCRyvNzYBlp1u0Luj00rfWeRWBWiIht6eqbafwNvbzs2rfQZQVCXahNaZCa90x8ZgfgVQhtdloE6FpFq_8fqj64cujFVs84wM5Vc2Y3t1AbKkFk8Z1lSrx4IBzTkkPRy-GaUGEgMVKFpfYhjDRXsjeoDrZWWXpJ_sHrmO0Fkynmo016lrAwjryVkkIS_RKkB5qeIV3Qq3T1sEbuHt2MJgZ8wuzyttW-451Lc4YBX1sFEsGe7HMH2A1Zb8LPvuWbvSncwXfskkM35ufiCfsRr0NaosEsoRld9TagIQTJiOx4UlTHRsSKbFedxFuM06Xuexxh9YfEI8Y9teNmNlu2m7RfeL05gmTJ3qRq1X8npAQbKoqIUDGEm8F56KlaPL9xrag4KVdOjUElkZzwpjN7jGFjciCx0SxML5t3jSl9L8SEEfJWPxoETzhfIK9vvRIx-eXtH0duIbQw3pjBysfGrpjKyubEVfovi6jLhawye55fZQkTj_EGVZOIrORx6dpUx4yrs7lgYsda_CabRtXzwi-8D1m_CqtFtSssfjvMTBjq99WU4X5AlPcLwQJZGFPsII9gLL1HriCcyplxV5iUh2d3I1EObx9PbXs2z67so_PT8gAQ91B-QWptVGfBxKn9SYQMjXEVXfJHbg6iCtnbVlwJowor2urwdUwDN1v0UwBNeoZPk7VgAEna_Lq64ExaY8AhoeZK1NGD5M5twSUfQ2FOfHJtFx64M2CEawY3Ty38zw9RnIdV3SeAUKkvcscPVH_QV1KzMRDbjBoOrVyueX4gwoXmLRX2WYzXP3j5dS4lwx9W6EIPy-ukTXSeyQcoJ_ybqMS8vfzzsKbVT-XMcuYANT_tjdeMOJGuyv77nMBtpuoUFFEz0E3LwbYHHsox-rZ_S_-kUqzRQoZQXjNfAq_q7mNm0gcSWPA269cKEWCxzMmU7soZNeCbxbikTAekn2iyesW_vAjcdw1TkGEC-lvC2Jmoln-BGODXwKqTOV2NDwvqVw6WtxpOdF5_OHQ_ZrvVFt7PpVIPWFJOGsJlGuVqyd9xfBtBZjIpi0EAAwpwSc0M3nLJOsRuzzrmz0wfqxsLkGT8fGcwPLU_bEpXL1_T5YyU-QGVLV-xTNR5UdJ5AfTkiD_kYZxW6hcDa6kfdvzCXFwyp43EwcaHwDAViWdcZs7kRjIoYr4Mcq8OYfVyOHcShvNg475pkvmbIkzZpU8bUK1QomXDCOo4ly0LbN9E7hniYAH0yh-Za37bPKzuOgjw0imlVqddQMxe6RyZL18iPxbvwDWzTo6vEi2JnpHNkzwzuN_sg_8hgSi8bKixM6nTA41X18Lz3WnY1F6araH1DasBgjIUWoCS6mELLlxaT5I4eQSppaQ17g1AMXOr7wZzXEPDQEOUhiYX2P1JfGmq93G1M44B_woquMl-fMFfTfo1qg0iNTffJp55azZ1tbhi0QMTwAmXXPkiDVoHsYrYNkD3qwrgxgTo1bbaYmOdmYNXgSS7u7shJq236f4CDzkLF0uP.PSX_-8Gtrm897LeRFydnwQ"
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
        hits = []
        for hit_json in res.json()["data"]["search"]["hits"]:

            id = hit_json["hit"]["contentId"]
            isProgram = True
            try:
                # film
                title = hit_json["hit"]["text"]["title"]["full"]["program"]["default"]["content"]

            except KeyError:
                # series
                isProgram = False
                title = hit_json["hit"]["text"]["title"]["full"]["series"]["default"]["content"]

            if isProgram:
                hitType = HitType.Film
                hit = Movie(title=title, id=id, type=hitType)

                internalTitle = hit_json["hit"]["internalTitle"]
                hit.info.internalTitle = internalTitle
                hit.format = hit_json["hit"]["mediaMetadata"]["format"]
                hit.mediaId = hit_json["hit"]["mediaMetadata"]["mediaId"]

                hit.length = hit_json["hit"]["mediaMetadata"]["runtimeMillis"]
                videoThumbnailURL = max(hit_json["hit"]["image"]["tile"].items(),
                                        key=lambda x: float(x[0]))[1]["video"]["default"]["url"]
            else:
                hitType = HitType.Series
                hit = Series(title=title, id=id, type=hitType)

                hit.seriesId = hit_json["hit"]["seriesId"]
                hit.encodedSeriesId = hit_json["hit"]["encodedSeriesId"]

                hit.familyId = hit_json["hit"]["family"]["familyId"]
                hit.encodedFamilyId = hit_json["hit"]["family"]["encodedFamilyId"]

                videoThumbnailURL = max(hit_json["hit"]["image"]["tile"].items(),
                                        key=lambda x: float(x[0]))[1]["series"]["default"]["url"]

            hit.info.releaseType = hit_json["hit"]["releases"][0]["releaseType"]
            hit.info.releaseDate = hit_json["hit"]["releases"][0]["releaseDate"]
            hit.info.releaseYear = hit_json["hit"]["releases"][0]["releaseYear"]
            hit.info.ImpliedMaturityValue = hit_json["hit"]["ratings"][0]["impliedMaturityValue"]
            hit.info.rating = hit_json["hit"]["ratings"][0]["value"]

            hit.info.videoThumbnailURL = videoThumbnailURL
            hits.append(hit)
        if not hits:
            logger.warning("No hits found, response:\n%s", res.text)
        return hits

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
            id = profile["id"]
            name = profile["name"]
            kidsMode = profile["attributes"]["kidsModeEnabled"]
            isDefault = profile["attributes"]["isDefault"]

            prf = Profile(id=id, name=name, kidsMode=kidsMode, isDefault=isDefault)
            prf.avatar.id = profile["attributes"]["avatar"]["id"]
            prf.avatar.userSelected = profile["attributes"]["avatar"]["userSelected"]
            prf.languagePreferences.app = profile["attributes"]["languagePreferences"]["appLanguage"]

            prf.languagePreferences.playback = profile["attributes"]["languagePreferences"]["playbackLanguage"]

            prf.languagePreferences.subtitle = profile["attributes"]["languagePreferences"]["subtitleLanguage"]
            prf.languagePreferences.subsEnabled = profile["attributes"]["languagePreferences"]["subtitlesEnabled"]
            profiles.append(prf)
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
        profile = res.json()["data"]["me"]["account"]["activeProfile"]
        id = profile["id"]
        name = profile["name"]
        kidsMode = profile["attributes"]["kidsModeEnabled"]
        isDefault = profile["attributes"]["isDefault"]

        prf = Profile(id=id, name=name, kidsMode=kidsMode, isDefault=isDefault)
        prf.avatar.id = profile["attributes"]["avatar"]["id"]
        prf.avatar.userSelected = profile["attributes"]["avatar"]["userSelected"]

        prf.languagePreferences.playback = profile["attributes"]["languagePreferences"]["playbackLanguage"]

        prf.languagePreferences.subtitle = profile["attributes"]["languagePreferences"]["subtitleLanguage"]
        prf.languagePreferences.subsEnabled = profile["attributes"]["languagePreferences"]["subtitlesEnabled"]
        return prf

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


api = DisneyAPI(email="email", password="password", proxies={})
api.setLanguage(Language.Polish)
cloneWars = api.search("clone wars")[0]
print(cloneWars.getRelated())
# TODO ATRYBUTY!