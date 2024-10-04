from ..Auth import Auth
from ..Config import APIConfig
from ..models.Hit import Hit
from ..models.HitType import HitType
from ..models.Season import Season
from ..utils.parser import parse_participants, parse_hits


class Series(Hit):

    def __init__(self, title, series_id, hit_type: HitType):
        super().__init__(title, series_id, hit_type)
        self.series_id = None
        self.encoded_series_id = None

    def get_seasons(self):
        return self._get_more_data()

    def _get_more_data(self):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encoded_series_id}")

        res_json = res.json()["data"]["DmcSeriesBundle"]
        self._full_description = res_json["series"]["text"]["description"]["full"]["series"]["default"]["content"]
        self._medium_description = res_json["series"]["text"]["description"]["medium"]["series"]["default"]["content"]
        self._brief_description = res_json["series"]["text"]["description"]["brief"]["series"]["default"]["content"]

        actors, directors, producers, creators = parse_participants(res_json["series"]["participant"])
        self._cast = actors
        self._directors = directors
        self._producers = producers
        self._creators = creators

        seasons = []
        for season_json in res_json["seasons"]["seasons"]:
            season_id = season_json["seasonId"]
            number = season_json["seasonSequenceNumber"]

            season = Season(season_id=season_id, number=number)

            season.release_date = season_json["releases"][0]["releaseDate"]
            season.release_year = season_json["releases"][0]["releaseYear"]
            season.rating = season_json["ratings"][0]["value"]
            season.encoded_series_id = season_json["encodedSeriesId"]
            season.series_id = season_json["seriesId"]

            seasons.append(season)

        return seasons

    def get_related(self):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/RelatedItems/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encoded_series_id}")

        return parse_hits(res.json()["data"]["RelatedItems"]["items"])
