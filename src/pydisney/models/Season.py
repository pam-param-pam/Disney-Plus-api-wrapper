from ..Auth import Auth
from ..Config import APIConfig
from ..Exceptions import ApiException

from ..models.Episode import Episode
from ..utils.parser import parse_audio_and_subtitles


class Season:
    def __init__(self, season_id: str, number: int):
        self.encoded_series_id = None
        self.series_id = None
        self.release_date = None
        self.release_year = None
        self.rating = None
        self.id = season_id
        self.number = number

    def get_episodes(self):
        res = Auth.make_get_request(f"https://disney.content.edge.bamgrid.com/svc/content/DmcEpisodes/version/5.1/region/{APIConfig.region}/audience/false/maturity/1850/language/{APIConfig.language}/seasonId/{self.id}/pageSize/60/page/1")

        if res.status_code != 200:
            raise ApiException(res)
        episodes = []
        for episode_json in res.json()["data"]["DmcEpisodes"]["videos"]:
            content_id = episode_json["contentId"]
            number = episode_json["episodeSeriesSequenceNumber"]
            title = episode_json["text"]["title"]["full"]["program"]["default"]["content"]
            video_id = episode_json["videoId"]
            episode = Episode(content_id=content_id, number=number, title=title, video_id=video_id)

            episode.season_number = self.number
            episode.internal_title = episode_json["internalTitle"]
            episode.media_id = episode_json["mediaMetadata"]["mediaId"]
            episode.original_language = episode_json["originalLanguage"]
            episode.length = episode_json["mediaMetadata"]["runtimeMillis"]
            episode.format = episode_json["mediaMetadata"]["format"]
            episode.rating = episode_json["ratings"][0]["value"]
            episode.brief_description = episode_json["text"]["description"]["brief"]["program"]["default"]["content"]
            episode.medium_description = episode_json["text"]["description"]["medium"]["program"]["default"]["content"]
            episode.full_description = episode_json["text"]["description"]["full"]["program"]["default"]["content"]

            audio_tracks, captions = parse_audio_and_subtitles(episode_json, episode.media_id)

            episode.subtitles = captions
            episode.audio_tracks = audio_tracks
            episodes.append(episode)
        return episodes

    def __str__(self):
        return f"[Id={self.id}, Number={self.number}]"

    def __repr__(self):
        return str(self.number)
