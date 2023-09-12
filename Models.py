from enum import Enum

from abc import ABC

from Config import APIConfig
from Exceptions import ApiException

class MetaData:
    def __init__(self):
        self.internalTitle = None
        self.releaseType = None
        self.releaseDate = None
        self.releaseYear = None
        self.ImpliedMaturityValue = None
        self.BgThumbnailUrl = None
        self.videoThumbnailURL = None
        self.rating = None

    def __str__(self):
        return (
            f"Internal Title={self.internalTitle}, Release Type={self.releaseType}, "
            f"Release Date={self.releaseDate}, Release Year={self.releaseYear}, "
            f"Implied Maturity Value={self.ImpliedMaturityValue}, "
            f"Background Thumbnail URL={self.BgThumbnailUrl}, "
            f"Video Thumbnail URL={self.videoThumbnailURL}, Rating={self.rating}, "

        )


class HitType(Enum):
    Film = "Film"
    Series = "Series"


class Hit(ABC):

    def __init__(self, title, id, type: HitType):
        self.info = MetaData()
        self.title = title
        self.id = id
        self.type = type

    def __str__(self):
        return f"[Title={self.title}, Type={self.type.value}]"

    def __repr__(self):
        return self.title


class Movie(Hit):

    def __init__(self, title, id, type: HitType):
        super().__init__(title, id, type)
        self.length = None
        self.mediaId = None
        self.format = None

    def download(self):
        pass




class Season:
    def __init__(self, id, number: int):
        self.encodedSeriesId = None
        self.seriesId = None
        self.releaseDate = None
        self.releaseYear = None
        self.rating = None
        self.id = id
        self.number = number

    def getEpisodes(self):
        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/DmcEpisodes/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/seasonId/{self.id}/pageSize/60/page/1",
            headers={"authorization": "Bearer " + APIConfig.token})

        if res.status_code != 200:
            raise ApiException(res)
        episodes = []
        for episode_json in res.json()["data"]["DmcEpisodes"]["videos"]:
            id = episode_json["contentId"]
            number = episode_json["episodeSeriesSequenceNumber"]
            title = episode_json["text"]["title"]["full"]["program"]["default"]["content"]
            videoId = episode_json["videoId"]
            episode = Episode(id=id, number=number, title=title, videoId=videoId)

            episode.internalTitle = episode_json["internalTitle"]
            episode.mediaId = episode_json["mediaMetadata"]["mediaId"]
            episode.originalLanguage = episode_json["originalLanguage"]
            episode.length = episode_json["mediaMetadata"]["runtimeMillis"]
            episode.format = episode_json["mediaMetadata"]["format"]
            episode.rating = episode_json["ratings"][0]["value"]
            episodes.append(episode)
        return episodes

    def __str__(self):
        return f"[Id={self.id}, Number={self.number}]"

    def __repr__(self):
        return str(self.number)


class Episode:
    def __init__(self, id, number: int, title, videoId):
        self.id = id
        self.number = number
        self.title = title
        self.videoId = videoId
        self.internalTitle = None
        self.mediaId = None
        self.length = None
        self.rating = None
        self.originalLanguage = None
        self.format = None

    def __str__(self):
        return f"[Title={self.title}, Id={self.id}, Number={self.number}]"

    def __repr__(self):
        return str(self.title)

    def download(self):
        pass
class AudioTracks:
    pass


class Captions:
    pass


class Series(Hit):

    def __init__(self, title, id, type: HitType):
        super().__init__(title, id, type)
        self.seriesId = None
        self.encodedSeriesId = None
        self.familyId = None
        self.encodedFamilyId = None
        self._fullDescription = None
        self._mediumDescription = None
        self._briefDescription = None

    def getFullDescription(self):
        if not self._fullDescription:
            self.getSeasons()
        return self._fullDescription

    def getMediumDescription(self):
        if not self._mediumDescription:
            self.getSeasons()
        return self._mediumDescription

    def getBriefDescription(self):
        if not self._briefDescription:
            self.getSeasons()
        return self._briefDescription

    def getSeasons(self):
        res = APIConfig.session.get(
            f"https://disney.content.edge.bamgrid.com/svc/content/DmcSeriesBundle/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/encodedSeriesId/{self.encodedSeriesId}",
            headers={"authorization": "Bearer " + APIConfig.token})

        if res.status_code != 200:
            raise ApiException(res)
        seasons = []
        json_res = res.json()["data"]["DmcSeriesBundle"]
        self._fullDescription = json_res["series"]["text"]["description"]["full"]["series"]["default"]["content"]
        self._mediumDescription = json_res["series"]["text"]["description"]["medium"]["series"]["default"]["content"]
        self._briefDescription = json_res["series"]["text"]["description"]["brief"]["series"]["default"]["content"]
        for season_json in json_res["seasons"]["seasons"]:
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
        hits = []
        for hit_json in res.json()["data"]["RelatedItems"]["items"]:

            id = hit_json["contentId"]
            isProgram = True
            try:
                # film
                title = hit_json["text"]["title"]["full"]["program"]["default"]["content"]

            except KeyError:
                # series
                isProgram = False
                title = hit_json["text"]["title"]["full"]["series"]["default"]["content"]

            if isProgram:
                hitType = HitType.Film
                hit = Movie(title=title, id=id, type=hitType)

                internalTitle = hit_json["internalTitle"]
                hit.info.internalTitle = internalTitle
                hit.format = hit_json["mediaMetadata"]["format"]
                hit.mediaId = hit_json["mediaMetadata"]["mediaId"]

                hit.length = hit_json["mediaMetadata"]["runtimeMillis"]
                videoThumbnailURL = max(hit_json["image"]["tile"].items(),
                                        key=lambda x: float(x[0]))[1]["program"]["default"]["url"]
            else:
                hitType = HitType.Series
                hit = Series(title=title, id=id, type=hitType)

                hit.seriesId = hit_json["seriesId"]
                hit.encodedSeriesId = hit_json["encodedSeriesId"]

                hit.encodedFamilyId = hit_json["family"]["encodedFamilyId"]

                videoThumbnailURL = max(hit_json["image"]["tile"].items(),
                                        key=lambda x: float(x[0]))[1]["series"]["default"]["url"]

            hit.info.releaseType = hit_json["releases"][0]["releaseType"]
            hit.info.releaseDate = hit_json["releases"][0]["releaseDate"]
            hit.info.releaseYear = hit_json["releases"][0]["releaseYear"]
            hit.info.rating = hit_json["ratings"][0]["value"]

            hit.info.videoThumbnailURL = videoThumbnailURL
            hits.append(hit)

        return hits


class Rating(Enum):
    Adult = "1850"
    Teen = "1650"
    Kid = "9999"

    Age18Plus = "1850"
    Age16Plus = "1650"
    Age14Plus = "1450"
    Age12Plus = "1250"
    Age9Plus = "950"
    Age6Plus = "650"
    Age0Plus = "10"


class Language(Enum):
    Albanian = "sq"
    Arabic = "ar"
    Catalan = "ca"
    Dutch = "nl"
    Bosnian = "bs"
    Bulgarian = "bg"
    Croatian = "hr"
    Czech = "cs"
    Danish = "da"
    Estonian = "et"
    Finnish = "fi"
    French = "fr"
    German = "de"
    Greek = "el"
    Hungarian = "hu"
    Icelandic = "is"
    Irish = "ga"
    Hebrew = "he"
    Italian = "it"
    Serbian = "sr"
    Lithuanian = "lt"
    Maltese = "mt"
    Macedonian = "mk"
    Norwegian = "no"
    Polish = "pl"
    Portuguese = "pt"
    Romanian = "ro"
    Slovak = "sk"
    Slovenian = "sl"
    English = "en"
    Spanish = "es"
    Swedish = "sv"
    Turkish = "tr"


class Account:
    def __init__(self, id, email, isEmailVerified, country, createdAt):
        self.id = id
        self.email = email
        self.isEmailVerified = isEmailVerified
        self.country = country
        self.createdAt = createdAt


class LanguagePreferences:
    def __init__(self):
        self.playback = None
        self.subtitle = None
        self.subsEnabled = None
        self.app = None


class Avatar:
    def __init__(self):
        self.id = None
        self.userSelected = None


class Profile:
    def __init__(self, id, name, kidsMode, isDefault):
        self.id = id
        self.name = name
        self.kidsMode = kidsMode
        self.avatar = Avatar()
        self.isDefault = isDefault
        self.languagePreferences = LanguagePreferences()

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.name
