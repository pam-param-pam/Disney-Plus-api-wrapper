from Config import APIConfig
from Exceptions import ApiException
from models.AudioTrack import AudioTrack
from models.Caption import Caption
from models.Hit import Hit
from models.HitType import HitType
from utils.parser import parseParticipants, parseHits, parseAudioCaptions


class Movie(Hit):

    def __init__(self, title, id, type: HitType):
        super().__init__(title, id, type)
        self.length = None
        self.mediaId = None
        self.format = None
        self._captions = None
        self._audioTracks = None
        self.internalTitle = None

    @property
    def captions(self):
        if not self._cast:
            self._getMoreData()
        return self._captions

    @property
    def audioTracks(self):
        if not self._audioTracks:
            self._getMoreData()
        return self._audioTracks

    def _getMoreData(self):
        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/DmcVideoBundle/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedFamilyId/{self.encodedFamilyId}",
            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)
        res_json = res.json()["data"]["DmcVideoBundle"]
        self._briefDescription = res_json["video"]["text"]["description"]["brief"]["program"]["default"]["content"]
        self._mediumDescription = res_json["video"]["text"]["description"]["medium"]["program"]["default"]["content"]
        self._fullDescription = res_json["video"]["text"]["description"]["full"]["program"]["default"]["content"]
        self.images = res_json["video"]["image"]
        actors, directors, producers, creators = parseParticipants(res_json["video"]["participant"])
        self._cast = actors
        self._directors = directors
        self._producers = producers
        self._creators = creators

        audioTracks, captions = parseAudioCaptions(res_json["video"], self.mediaId)

        self._captions = captions
        self._audioTracks = audioTracks

    def getRelated(self):

        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/RelatedItems/version/5.1/region/{APIConfig.region}/audience/k-false,l-true/maturity/1850/language/{APIConfig.language}/encodedFamilyId/{self.encodedFamilyId}",
            headers={"authorization": "Bearer " + APIConfig.token})
        if res.status_code != 200:
            raise ApiException(res)

        return parseHits(res.json()["data"]["RelatedItems"]["items"])

    def download(self):
        pass
