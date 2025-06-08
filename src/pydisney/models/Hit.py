import logging
from abc import ABC
from typing import List, Optional

from ..Auth import Auth
from ..models.Downloable import MediaTrackSelector
from ..models.Season import Season
from ..utils.parser import safe_get

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
        self.__resource_id: Optional[str] = None
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
    def resourceId(self):
        if not self.is_movie:
            raise ValueError("Series has no resourceId property")
        if not self.__resource_id:
            self._get_playback_info()
        return self.__resource_id

    def _get_playback_info(self):
        url = "https://disney.api.edge.bamgrid.com/explore/v1.9/deeplink?action=playback&refId=9a280e53-fcc0-4e17-a02c-b1f40913eb0b&refIdType=deeplinkId"
        res = Auth.make_request("GET", url)
        self.__resource_id = res["data"]["deeplink"]["actions"][0]["resourceId"]

    def _get_more_data(self) -> None:
        url = f"https://disney.api.edge.bamgrid.com/explore/v1.9/page/entity-{self.id}"
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

    def _get_m3u8_url(self):
        playback_link = "https://disney.playback.edge.bamgrid.com/v7/playback/ctr-regular"
        data = {"playback": {"attributes": {}}, "playbackId": self.resourceId}

        headers = {
            "x-bamsdk-client-id": "disney-svod-9zmsiwec",
            "x-bamsdk-platform": "javascript/windows/chrome",
            "x-bamsdk-version": "32.6",
            "x-dss-edge-accept": "vnd.dss.edge+json; version=2",
            "x-dss-feature-filtering": "true",
            "x-application-version": "1.1.2"
        }

        res = Auth.make_request("POST", playback_link, data=data, headers=headers)
        return res['stream']['sources'][0]['complete']["url"]

    def get_tracks(self) -> MediaTrackSelector:
        url = self._get_m3u8_url()
        return MediaTrackSelector(self.title, url)

    def __str__(self):
        return f"[Title={self.title}]"

    def __repr__(self):
        return self.title
