import os
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import m3u8

from Config import APIConfig
from Exceptions import ApiException


class Downloadable(ABC):

    def __init__(self, mediaId):
        self.default_path = APIConfig.default_path
        self.mediaId = mediaId

    @abstractmethod
    def download(self):
        pass

    def get_m3u8_url(self, media_id):
        headers = {
            'accept': 'application/vnd.media-service+json; version=6',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            'x-bamsdk-platform': "macOS",
            'x-bamsdk-version': '23.1',
            'x-dss-edge-accept': 'vnd.dss.edge+json; version=2',
            'x-dss-feature-filtering': 'true',
            'Origin': 'https://www.disneyplus.com',
            'authorization': APIConfig.token
        }
        playback_url = f"https://disney.playback.edge.bamgrid.com/media/{media_id}/scenarios/tvs-drm-cbcs"

        json_data = {
            'playback': {
                'attributes': {
                    'resolution': {
                        'max': [
                            '1920x1080',
                        ],
                    },
                    'protocol': 'HTTPS',
                    'assetInsertionStrategy': 'SGAI',
                    'playbackInitiationContext': 'ONLINE',
                    'frameRates': [
                        60,
                    ],
                    'slugDuration': 'SLUG_500_MS',
                }
            },
        }
        res = APIConfig.session.post(
            url=playback_url, headers=headers, json=json_data)
        if res.status_code != 200:
            raise ApiException(res)

        return res.json()['stream']['sources'][0]['complete']["url"]

    def parse_m3u(self, m3u_link, language):
        base_url = os.path.dirname(m3u_link)

        subtitle = {}
        audio = {}
        playlists = m3u8.load(uri=m3u_link).playlists

        quality_list = [
            playlist.stream_info.bandwidth for playlist in playlists]
        best_quality = quality_list.index(min(quality_list))
        for media in playlists[best_quality].media:
            print(media)
            if media.language == language:

                if media.type == 'SUBTITLES' and media.group_id == 'sub-main':

                    subtitle = {'m3u8_url': urljoin(media.base_uri, media.uri), 'lang': media.language, 'urls': []}

                    segments = m3u8.load(subtitle['m3u8_url'])
                    for uri in segments.files:
                        subtitle['urls'].append(urljoin(segments.base_uri, uri))

                if media.type == 'AUDIO' and 'Audio Description' not in media.name:
                    audio = {'url': f'{base_url}/{media.uri}'}
                    if media.group_id == 'eac-3':
                        audio['extension'] = '.eac3'
                    elif media.group_id in ['aac-128k', 'aac-64k']:
                        audio['url'] = f'{base_url}/{media.uri}'
                        audio['extension'] = '.aac'
                    audio['lang'] = media.language

        return subtitle, audio
