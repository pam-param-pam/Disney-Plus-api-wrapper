from Config import APIConfig
from Exceptions import ApiException
from models.Episode import Episode
from utils.parser import parseAudioCaptions


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
            episode.contentId = episode_json["contentId"]
            episode.briefDescription = episode_json["text"]["description"]["brief"]["program"]["default"]["content"]
            episode.mediumDescription = episode_json["text"]["description"]["medium"]["program"]["default"]["content"]
            episode.fullDescription = episode_json["text"]["description"]["full"]["program"]["default"]["content"]

            audioTracks, captions = parseAudioCaptions(episode_json)

            episode.captions = captions
            episode.audioTracks = audioTracks
            episodes.append(episode)
        return episodes

    def __str__(self):
        return f"[Id={self.id}, Number={self.number}]"

    def __repr__(self):
        return str(self.number)
