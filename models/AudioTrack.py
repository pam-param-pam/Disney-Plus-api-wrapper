import os

from models.Downloadable import Downloadable
from utils.io import download_audio


class AudioTrack(Downloadable):

    def __init__(self, language, name, mediaId, trackType, features):
        super().__init__(mediaId)
        self.language = language
        self.name = name
        self.trackType = trackType
        self.features = features

    def __str__(self):
        return f"[{self.name}, {self.language}]"

    def __repr__(self):
        return self.name

    def _get_audio(self, audio, name):

        path = os.path.join(self.default_path, name + audio['extension'])
        download_audio(audio['url'], path)
        return path

    def download(self, name=None):
        if not name:
            name = self.mediaId

        m3u8_url = self.get_m3u8_url(self.mediaId)

        subtitle, audio = self.parse_m3u(m3u8_url, self.language)

        return self._get_audio(audio, name)
