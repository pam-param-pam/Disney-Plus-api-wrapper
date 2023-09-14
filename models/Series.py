from Config import APIConfig
from Exceptions import ApiException
from models.Hit import Hit
from models.HitType import HitType
from models.Season import Season
from utils.parser import parseParticipants, parseHits


class Series(Hit):

    def __init__(self, title, id, type: HitType):
        super().__init__(title, id, type)
        self.seriesId = None
        self.encodedSeriesId = None

    def getSeasons(self):
        return self._getMoreData()

    def _getMoreData(self):
        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encodedSeriesId}",
            headers={"authorization": "Bearer " + APIConfig.token})

        if res.status_code != 200:
            raise ApiException(res)

        res_json = res.json()["data"]["DmcSeriesBundle"]
        self._fullDescription = res_json["series"]["text"]["description"]["full"]["series"]["default"]["content"]
        self._mediumDescription = res_json["series"]["text"]["description"]["medium"]["series"]["default"]["content"]
        self._briefDescription = res_json["series"]["text"]["description"]["brief"]["series"]["default"]["content"]

        actors, directors, producers, creators = parseParticipants(res_json["series"]["participant"])
        self._cast = actors
        self._directors = directors
        self._producers = producers
        self._creators = creators

        seasons = []
        for season_json in res_json["seasons"]["seasons"]:
            id = season_json["seasonId"]
            number = season_json["seasonSequenceNumber"]

            season = Season(id=id, number=number)

            season.releaseDate = season_json["releases"][0]["releaseDate"]
            season.releaseYear = season_json["releases"][0]["releaseYear"]
            season.rating = season_json["ratings"][0]["value"]
            season.encodedSeriesId = season_json["encodedSeriesId"]
            season.seriesId = season_json["seriesId"]

            seasons.append(season)

        return seasons

    def getRelated(self):

        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/RelatedItems/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encodedSeriesId}",
            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        return parseHits(res.json()["data"]["RelatedItems"]["items"])
