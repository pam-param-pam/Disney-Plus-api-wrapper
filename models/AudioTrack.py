import os

from Config import APIConfig
from models.Downloadable import Downloadable
from utils.helper import rename_filename

class AudioTrack(Downloadable):

    def __init__(self, language, name, media_id, track_type, features):
        super().__init__(media_id)
        self.language = language
        self.name = name
        self.track_type = track_type
        self.features = features

    def __str__(self):
        return f"[{self.name}, {self.language}]"

    def __repr__(self):
        return self.name

    def _download_audio(self, m3u8_url, output):
        os.system(
            f'ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -report -i "{m3u8_url}" -c copy "{output}" -preset ultrafast -loglevel warning -hide_banner -stats')

    def _get_audio(self, audio, name):
        path = os.path.join(APIConfig.default_path, name + audio["extension"])
        self._download_audio(audio["url"], path)
        return path

    def download(self, name=None, quality="max"):
        if not name:
            name = self.media_id
        name = rename_filename(name)
        m3u8_url = self._get_m3u8_url(self.media_id)

        _, audio = self._parse_m3u(m3u8_url, self.name, quality)

        return self._get_audio(audio, name)
