import logging
from abc import ABC
from typing import List, Optional

from src.pydisney.Auth import Auth
from src.pydisney.Config import APIConfig
from src.pydisney.models.Season import Season
from src.pydisney.utils.parser import safe_get

logger = logging.getLogger("pydisney")
logger = logger.getChild("Hit")


class Hit(ABC):

    def __init__(self, data):
        self.id: Optional[str] = None
        self.title: Optional[str] = None
        self.brief_desc: Optional[str] = None
        self.medium_desc: Optional[str] = None
        self.full_desc: Optional[str] = None
        self.genres: Optional[List[str]] = None
        self.rating: Optional[str] = None
        self.rating: Optional[str] = None
        self.artwork = None
        self.startYear: Optional[str] = None

        self.__seasons: List[Season] = []
        self.__is_movie: Optional[bool] = None
        self.__endYear: Optional[str] = None
        self.__credits: Optional[dict] = None
        self.__release_date: Optional[str] = None
        self.__length: Optional[int] = None
        self._parse_data(data)

    def _parse_data(self, data):

        self.id = data["id"]
        self.title = data["visuals"]["title"]
        self.brief_desc = safe_get(data, ["visuals", "description", "brief"])
        self.medium_desc = safe_get(data, ["visuals", "description", "medium"])
        self.full_desc = safe_get(data, ["visuals", "description", "full"])
        self.genres = safe_get(data, ["visuals", "metastringParts", "genres", "values"], [])
        self.rating = safe_get(data, ["visuals", "metastringParts", "ratingInfo", "rating", "text"])
        self.startYear = safe_get(data, ["visuals", "metastringParts", "releaseYearRange", "startYear"])
        self.artwork = safe_get(data, ["visuals", "artwork"])

    @staticmethod
    def parse_hits(data):
        hits = []
        for element in data:
            hits.append(Hit(element))
        return hits

    @property
    def is_movie(self):
        if self.__is_movie is None:
            self._get_more_data()
        return self.__is_movie

    @property
    def length(self):
        if not self.is_movie:
            raise ValueError("Series has no length property")
        if self.__length is None:
            self._get_more_data()
        return self.__length

    @property
    def seasons(self):
        if self.is_movie:
            raise ValueError("Movie has no seasons property")
        if not self.__seasons:
            self._get_more_data()
        return self.__seasons

    @property
    def credits(self):
        if not self.__credits:
            self._get_more_data()
        return self.__credits

    @property
    def endYear(self):
        if not self.__endYear:
            self._get_more_data()
        return self.__endYear

    @property
    def release_date(self):
        if not self.__release_date:
            self._get_from_old_api()
        return self.__release_date

    def _get_more_data(self) -> None:
        url = f"https://disney.api.edge.bamgrid.com/explore/v1.7/page/entity-{self.id}"
        res = Auth.make_request("GET", url)
        self.__is_movie = True
        for container in res["data"]["page"]["containers"]:
            if container["type"] == "episodes":
                self.__is_movie = False
                for index, season_data in enumerate(container["seasons"]):
                    self.__seasons.append(Season(season_data, index))

            elif container["type"] == "set":
                # ignoring suggested and extras for now
                pass

            elif container["type"] == "details":
                data = safe_get(container, ["visuals", "credits"])
                if data:
                    formatted_data = {}
                    for entry in data:
                        heading = entry['heading']
                        items = [item['displayText'] for item in entry['items']]
                        formatted_data[heading] = items
                    self.__credits = formatted_data
                self.__endYear = safe_get(container, ["visuals", "metastringParts", "releaseYearRange", "endYear"], ignoreError=True)
                self.__length = safe_get(container, ["visuals", "duration", "runtimeMs"])

    def _get_from_old_api(self) -> None:
        logger.info("Attempting to fetch data from old api")

        res = Auth.make_request("GET",
                                f"https://disney.content.edge.bamgrid.com/svc/search/disney/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/queryType/ge/pageSize/1/query/{self.title}")
        item = res["data"]["search"]["hits"][0]["hit"]

        self.__release_date = item["releases"][0]["releaseDate"]
        self.__encodedSeriesId = item["encodedSeriesId"]

    def _monkey_patch(self) -> None:
        pass
        # todo
        # res = Auth.make_request("GET",
        #     f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/encodedSeriesId/106A3s2Armta")
        # print(res)
        # res = Auth.make_get_request(
        #     f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encoded_series_id}")
        #
        # res_json = res.json()["data"]["DmcSeriesBundle"]
        # self._full_description = res_json["series"]["text"]["description"]["full"]["series"]["default"]["content"]
        # self._medium_description = res_json["series"]["text"]["description"]["medium"]["series"]["default"]["content"]
        # self._brief_description = res_json["series"]["text"]["description"]["brief"]["series"]["default"]["content"]
        #
        # actors, directors, producers, creators = parse_participants(res_json["series"]["participant"])
        # self._cast = actors
        # self._directors = directors
        # self._producers = producers
        # self._creators = creators
        #
        # seasons = []
        # for season_json in res_json["seasons"]["seasons"]:
        #     season_id = season_json["seasonId"]
        #     number = season_json["seasonSequenceNumber"]
        #
        #     season = Season(season_id=season_id, number=number)
        #
        #     season.release_date = season_json["releases"][0]["releaseDate"]
        #     season.release_year = season_json["releases"][0]["releaseYear"]
        #     season.rating = season_json["ratings"][0]["value"]
        #     season.encoded_series_id = season_json["encodedSeriesId"]
        #     season.series_id = season_json["seriesId"]
        #
        #     seasons.append(season)
        #
        # return seasons

    def __str__(self):
        return f"[Title={self.title}]"

    def __repr__(self):
        return self.title
