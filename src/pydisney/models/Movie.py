from ..Auth import Auth
from ..Config import APIConfig
from ..models.Hit import Hit
from ..models.HitType import HitType
from ..utils.parser import parse_participants, parse_hits, parse_audio_and_subtitles


class Movie(Hit):

    def __init__(self, title, movie_id, hit_type: HitType):
        super().__init__(title, movie_id, hit_type)
        self.length = None
        self.media_id = None
        self.format = None
        self._subtitles = None
        self._audio_tracks = None
        self.internal_title = None
        self.original_language = None

    @property
    def subtitles(self):
        if not self._subtitles:
            self._get_more_data()
        return self._subtitles

    @property
    def audio_tracks(self):
        if not self._audio_tracks:
            self._get_more_data()
        return self._audio_tracks

    def _get_more_data(self):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/DmcVideoBundle/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedFamilyId/{self.encoded_family_id}")
        res_json = res.json()["data"]["DmcVideoBundle"]
        self._brief_description = res_json["video"]["text"]["description"]["brief"]["program"]["default"]["content"]
        self._medium_description = res_json["video"]["text"]["description"]["medium"]["program"]["default"]["content"]
        self._full_description = res_json["video"]["text"]["description"]["full"]["program"]["default"]["content"]
        self.images = res_json["video"]["image"]
        actors, directors, producers, creators = parse_participants(res_json["video"]["participant"])
        self._cast = actors
        self._directors = directors
        self._producers = producers
        self._creators = creators

        audio_tracks, subtitles = parse_audio_and_subtitles(res_json["video"], self.media_id)

        self._subtitles = subtitles
        self._audio_tracks = audio_tracks

    def get_related(self):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/RelatedItems/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedFamilyId/{self.encoded_family_id}")
        return parse_hits(res.json()["data"]["RelatedItems"]["items"])
