import os
from abc import ABC, abstractmethod
from urllib.parse import urljoin

import m3u8

from ..Auth import Auth


class Downloadable(ABC):

    def __init__(self, media_id):
        self.media_id = media_id

    @abstractmethod
    def download(self):
        pass

    def _get_m3u8_url(self, media_id):

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
        res = Auth.make_post_request(playback_url, json=json_data)

        return res.json()['stream']['sources'][0]['complete']["url"]

    def _parse_m3u(self, m3u_link, name, quality):
        base_url = os.path.dirname(m3u_link)
        subtitle = {}
        audio = {}
        playlists = m3u8.load(uri=m3u_link).playlists

        quality_list = [
            playlist.stream_info.bandwidth for playlist in playlists]

        if quality.lower() == "max":
            quality = quality_list.index(max(quality_list))
        else:
            quality = quality_list.index(min(quality_list))

        for media in playlists[quality].media:
            if media.name == name:

                if media.type == 'SUBTITLES' and media.group_id == 'sub-main':

                    subtitle = {'m3u8_url': urljoin(media.base_uri, media.uri), 'lang': media.language, 'urls': []}

                    segments = m3u8.load(subtitle['m3u8_url'])
                    for uri in segments.files:
                        subtitle['urls'].append(urljoin(segments.base_uri, uri))
                        break

        for media in playlists[quality].media:
            if media.name == name:
                if media.type == 'AUDIO':
                    audio = {'url': f'{base_url}/{media.uri}'}
                    if media.group_id == 'eac-3':
                        audio['extension'] = '.eac3'
                    elif media.group_id in ['aac-128k', 'aac-64k']:
                        audio['url'] = f'{base_url}/{media.uri}'
                        audio['extension'] = '.aac'
                    audio['lang'] = media.language
                    break
        return subtitle, audio
