from typing import Optional, List

from .Episode import Episode
from ..Auth import Auth


class Season:
    def __init__(self, data, number):
        self.id: Optional[str] = None
        self.totalEpisodesCount: Optional[int] = None
        self.name: Optional[str] = None
        self.number: Optional[int] = number

        self.__episodes: Optional[List[Episode]] = []
        self._parse_data(data)

    def _parse_data(self, data):
        self.id = data["id"]
        self.totalEpisodesCount = data["visuals"]["episodeCountDisplayText"]
        self.name = data["visuals"]["name"]

    @property
    def episodes(self):
        if not self.__episodes:
            self._get_more_data()
        return self.__episodes

    def _get_more_data(self):
        url = f"https://disney.api.edge.bamgrid.com/explore/v1.7/season/{self.id}"
        res = Auth.make_pagination_request("GET", url)
        for page in res:
            for element in page["data"]["season"]["items"]:
                self.__episodes.append(Episode(element))
        return self.__episodes

    def __str__(self):
        return f"[name={self.name}]"

    def __repr__(self):
        return self.name
