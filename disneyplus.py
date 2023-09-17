#!/usr/bin/python3
# coding: utf-8

"""
This module is to download subtitle from Disney+
"""
import logging
import os
import shutil
import sys
from urllib.parse import urljoin
import m3u8
import requests

from utils.io import rename_filename, download_files, download_audio
from utils.subtitle import convert_subtitle, merge_subtitle_fragments

SUBTITLE_FORMAT = ['.srt', '.ass', '.ssa', '.vtt', '.xml']

logging.basicConfig()

logger = logging.getLogger('DisneyAPI')
logger.setLevel(logging.DEBUG)


class DisneyPlus:
    """
    Service code for DisneyPlus streaming service (https://www.disneyplus.com).

    Authorization: email & password
    """

    def __init__(self):

        self.audio_language = "en"
        self.access_token = "eyJ6aXAiOiJERUYiLCJraWQiOiJ0Vy10M2ZQUTJEN2Q0YlBWTU1rSkd4dkJlZ0ZXQkdXek5KcFFtOGRJMWYwIiwiY3R5IjoiSldUIiwiZW5jIjoiQzIwUCIsImFsZyI6ImRpciJ9..UGIulMeQ-6GMYBcK.lJplOJpXitjVdwQf9Gduk-s2UHxiQS393Ahvy_hFpuz-5HL6aAZpSSI9IsY52t5GQW_zEUGFWMmqCuRKCJtgKssSJS7dfFoW5mWWHmU49n1lFAljtzKE7vn0J1JRBA2ilx3-DYZYJRcf2N-H7k7X6tcnr14k4moQndvdVcGu2nUE1Nv7XDbqcE8A6jtY26UKxyLyraRwCIuaNdk_dAgw3B48gdxlKK_c-mURDQ1OHGz2gzCnkMZeiLDfJesG3LCODlYREVhrHUyKKE2EMj_hbUu1gQj1NIYdfugnFl1ViS_6EL9EMqgL-kv8NhAwCqGM8YA2NwS6NRrwFhQ_2yc4Kpm6UXunu9KQEiLGhQFx6DvcDHJSZW6POfo07Gfsn1cMld4voaJEvlT5xTQdUrwOz_PgLUZF91R5YvhzDw7KbZPKS1SggCLfGIOjHX-2J-FoKv0SA4j4zO3VKcRHTUdCLNE4nuLwZxo64XkXcr4L96YK81MYskPaJj-qPbDn8bLJnOZpuh4CpDI-EXlxyjYtTFDJ8flLMllrNnvQiEnxxswXl4kA0X3Ee9ANeOQOHvDvT1G6kld2WCYwiuxFT5WMpagTnhfqVyxjKsnF-lbRzqe9xsbFX7Cnv8yx8qMYogqQ24qniXSR7Qv87OyrKItJZt4nFq8G_Ju5SpX1qvx9t-x3FXsYrqM_vIxi8kJKVDOv-mQCqQS7EgssJjmFD5MAinE5AvjyDGGlfi11GVlVYoaCFzBN9xMyPrg6Nd23jirEr8IzgVocRUdQcbPd2YtvuJk2wqVDI-v-kQl8ARRAJpc8pWfnOsq6zJLIdRW9EoL4CIj2jGiW4CoTtIx9y9RRB2cQmCRO__0geFFARnf_ElS1IIorf4KX_ipRI5DSghwc4_sOXU2OoVIDg-8YI6cm5MoWsUgE_ohrSrjT_EHHzw7MqWJ9xLO2YoEK9MEl3rkcoEpvhgJc6rjGCtzghuk-ZZ0gcpt2Q-6Ka2qEqDhpTOJuxf_NT-gc_4d1QdqFrx5B7Uuchvkoxt6-A1BDaB8uU7swtnZT4D9fgZ9PiVok59FejaMpi8RjctIWt4m_TClXUlx9UexDi1wi8Ks-gARYUbSYeSiiAdoMFWa0rTTwdrB74z9CF1aSQ0_iZj_BqbzR6nzcvOccQX2QHUNhTDaoZ-9bZFLkwC-CuxeTeRo3HV-oK6AeXgBWtuwWP8sB8NWdHcZmMXMn_CVyj8FtepKNEMwJfeI-ytC7kq5CsMYXwmguSZMNzOxDcpXfOjhZUh7frm8BbXITGGVzA6VTPykB1osashl127IQWWLVH0dHMTrIItP27UO0Es_9yhFp0ulUreDXYWJ4rIq3pzqTG03rkye9Aqa0j0BrU5ij08b584U5LxOARbSsTh2Lbm_pWu-j65TDpmreHREf6dm0CcMXbQYL9LJuq9hbAiB-WggoR8vPytmhVLC_x2PcCMObzOYke2QJNA9C8gPn3zlqJOp9qkOiTzHAYfxYy4J4nSjNquf9xid8KszaeD6zvYllYvsCQvUp4WFAynpPzvBwLzX4GetFGnG6w-YqSCAlrX00UhYbK8Vi6DgdyrhqMaogOLqel0U_-Dj4h2lBPrZHD3EXsJlMEe7BGH7OMY8IC-n9NCINEPm41tjOlTUAgqa79RKWOW12etxkCJybWa6U6aHP6BPGrp2Glyju-Lb5mPf_ArX5vtMb7dUaooBmZsr8j9FftQf96YLxtnBhlNyCcj4Y5HbkC2qXKgQexehhFxQZOZd1gTEllf3xAiirHNLp6SFLLHQWNjMl9PRSrLHqXoN_CMSyrDz_4ETQpBetWxJLEGtFmIkdCq9VCT75IOTh-9ur9Hfu4J_iHxjXRlca71tMGFQ_PmDvG8ikSI6XWuxErwCvh2teav56UoodkJKacbby3nVn5ki9rL3_ZTy-K7875lMcJuWalzoPPMdzYvHpK8UdjEjI-apdCb7ekb3KiMUse8ZWiTOZx8vcOQQYMeoX_1PzRIfa2KEOjU7XAKQ4QtWr2kH2kMPnRhahV_F6DiU_k0VXoD74SR-NJ3rH5Tj-PMuDKeXJOGlAOqyIoA-M23EOVu4epXMoUYx8S2_6gtlsHBhbIcueSiF9xXhqo4wAV8jF_5nFvzEFnCWGRFZs4L5msi8dzfM3_IDzx2fVmRcp-KatAJBZQydPN3YkoFwHLEcBr_OslYErDu294BAVOAcI49e_XwfaxCEP2poQ5DUvGpfod1WSlCzcDUjUBQsosjGMBYX6pW8-WupOvewT9NAgYdmNCfkq23jNe8YCovx4V9RW23IT2gQAfIs0ZpzUwh3FJpEwG71I0T_QqccHp2S-Uke9dgv4Y1U7D2Xmj1wQ9xO1TaJfXArVJNCADVV2MlT7l4Gv81a55tD25scp8AT2eJKjmFhEYOwNn9qAjafwo2-QqE3DajaOR0l0Dyzjyyb33RlfrVSg6GcWRxX8GW9abeSJoUAAWSjsqgxva1VFRvQ0ZejbK9J3J0x-CYsphNmNqcIONehBW-nrXhpiDd4SPUgf8NYsR0BRJCmw7Qcl6xtGnq4fGHqTp590idyT-H8awCBRPqPZvaHi-NXYFznamTXLOepUExK7I75cNLr4i_vSbjGcMfkGol5HBPSErccOqNK87_AQ93x0vamY2M5Gok4_Ul8PNU_5tvCpqUyCP9TR6GVTy0TuTq52DrdjmezswIC0E21l06iED9IdrJmeW4FmBBqlWQjn2LJafVIFIUfT4n1iChs7pyorPUpGFi68Ss3okOUNsWG0InfUCb1_3Kl5j-KV92W94W-xfDyJCucxPztp6kWxBbmzWyKNsY6rumde7zDU5iW7k6WCjXArIgYRJSNnrZet_nHo_IrYDe_PZ12HzqqWlmShoYVSie5Ro0fwdXAULL6gbAyp0kgOFg5SVqbvlh9aK5KS6uD9lAB8fCtiUU51TrBpnEziIQoUFTjzc3e-hjooynGEbCgFv3HyHcNYAMGaUGXDY-41zmb_ecIZj3TQ0eyOixD3-3JF3BNBQu4TTwf7nIK-iA31q7cK_dyLieQ4T5iGBbA_MO5I7lm-c0Bm2jFAyQ0LKIEgJMUb5QRT7i2lZdUADo3NZY-W7aGMmiMMpvS-_KoE6hIW2dC_X63UfxpcX1NIVSTciHlWg1MzT1dPuIYwvHtSIR756hcgbKzSzBDtytjgNh268MtfLluMMjGgHGyWJhYEaihjJeHh4rVV0kwaJdX5T0yvAcPiTmLT_F19iZO2krG9eOhwixkhlLTYShpMNRJr7pup7h9m3flwcTZ0mZZ6z5WE.Wi2nlGiI0T_9UaBGDJzu0g"
        self.logger = logger
        self.platform = "DisneyPlus"
        self.download_path = ""
        self.subtitle_format = ".srt"
        self.session = requests.Session()

        self.subtitle_language = "en"

    """
    def movie_subtitle(self):
        movie_url = self.config['api']['DmcVideo'].format(
            region=self.profile['region'],
            language=self.profile['language'],
            family_id=os.path.basename(self.url))
        res = self.session.get(url=movie_url, timeout=5)
        if res.ok:
            data = res.json()['data']['DmcVideoBundle']['video']
            title = data['text']['title']['full']['program']['default']['content'].strip(
            )
            release_year = next(
                release['releaseYear'] for release in data['releases'] if release['releaseType'] == 'original')

            self.logger.info("\n%s (%s)", title, release_year)
            title = rename_filename(f'{title}.{release_year}')

            folder_path = os.path.join(self.download_path, title)
            if os.path.exists(folder_path):
                shutil.rmtree(folder_path)

            program_type = data['programType']

            media_id = data['mediaMetadata']['mediaId']
            m3u8_url = self.get_m3u8_url(media_id)

            filename = f'{title}.{release_year}.WEB-DL.{self.platform}.vtt'

            subtitle_list, audio_list = self.parse_m3u(m3u8_url)

            if not subtitle_list:
                self.logger.error("\nNo subtitles found!")
                sys.exit(1)

            self.logger.info("\nDownload: %s\n---------------------------------------------------------------", filename)
            self.get_subtitle(subtitle_list, program_type,
                              folder_path, filename)
            if self.audio_language:
                self.get_audio(audio_list, folder_path, filename)

            convert_subtitle(folder_path=folder_path,
                             platform=self.platform, subtitle_format=self.subtitle_format, locale=self.locale)
        else:
            self.logger.error(res.text)
    """

    def series_subtitle(self):

        title = "test"
        season_index = 2
        episode_index = 1
        program_type = "SERIES"
        name = rename_filename(
            f'{title}.S{str(season_index).zfill(2)}')
        folder_path = os.path.join(self.download_path, name)

        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

        m3u8_url = self.get_m3u8_url("94228b88-6cfb-44f6-98b6-d1f33e5a203e")
        self.logger.debug(m3u8_url)

        filename = f'{name}E{str(episode_index).zfill(2)}.WEB-DL.{self.platform}.vtt'
        subtitle_list, audio_list = self.parse_m3u(
            m3u8_url)

        if not subtitle_list:
            self.logger.error("\nNo subtitles found!")
            sys.exit(1)

        self.logger.info("\nDownload: %s\n---------------------------------------------------------------", filename)
        self.get_subtitle(subtitle_list, program_type,
                          folder_path, filename)
        if self.audio_language:
            self.get_audio(
                audio_list, folder_path, filename)

        convert_subtitle(folder_path=folder_path,
                         platform=self.platform, subtitle_format=self.subtitle_format)

    def get_m3u8_url(self, media_id):
        headers = {
            'accept': 'application/vnd.media-service+json; version=6',
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
            'x-bamsdk-platform': "macOS",
            'x-bamsdk-version': '23.1',
            'x-dss-edge-accept': 'vnd.dss.edge+json; version=2',
            'x-dss-feature-filtering': 'true',
            'Origin': 'https://www.disneyplus.com',
            'authorization': self.access_token
        }
        playback_url = f"https://disney.playback.edge.bamgrid.com/media/{media_id}/scenarios/tvs-drm-cbcs"

        self.logger.debug("playback url: %s", playback_url)

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
        res = self.session.post(
            url=playback_url, headers=headers, json=json_data, timeout=10)
        if res.ok:
            data = res.json()['stream']['sources'][0]['complete']
            self.logger.debug(data)
            return data['url']
        else:
            self.logger.error(res.text)
            sys.exit(1)

    def parse_m3u(self, m3u_link):
        base_url = os.path.dirname(m3u_link)
        sub_url_list = []
        languages = set()
        audio_url_list = []

        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36",
        }

        playlists = m3u8.load(uri=m3u_link, headers=headers).playlists
        self.logger.debug("playlists: %s", playlists)

        quality_list = [
            playlist.stream_info.bandwidth for playlist in playlists]
        best_quality = quality_list.index(max(quality_list))

        for media in playlists[best_quality].media:

            if media.type == 'SUBTITLES' and media.group_id == 'sub-main':
                if media.language:
                    sub_lang = media.language
                if media.forced == 'YES':
                    sub_lang += '-forced'

                sub = {}
                sub['lang'] = sub_lang
                sub['m3u8_url'] = urljoin(media.base_uri, media.uri)
                languages.add(sub_lang)
                sub_url_list.append(sub)

            if self.audio_language and media.type == 'AUDIO' and not 'Audio Description' in media.name:
                audio = {}
                if media.group_id == 'eac-3':
                    audio['url'] = f'{base_url}/{media.uri}'
                    audio['extension'] = '.eac3'
                elif media.group_id == 'aac-128k':
                    audio['url'] = f'{base_url}/{media.uri}'
                    audio['extension'] = '.aac'
                audio['lang'] = media.language
                self.logger.debug(audio['url'])
                audio_url_list.append(audio)

        subtitle_list = []
        for sub in sub_url_list:
            if sub['lang'] in self.subtitle_language:
                subtitle = {}
                subtitle['lang'] = sub['lang']
                subtitle['urls'] = []
                segments = m3u8.load(sub['m3u8_url'])
                for uri in segments.files:
                    subtitle['urls'].append(urljoin(segments.base_uri, uri))
                subtitle_list.append(subtitle)

        return subtitle_list, audio_url_list

    def get_subtitle(self, subtitle_list, program_type, folder_path, sub_name):

        languages = set()
        subtitles = []

        for sub in subtitle_list:
            filename = sub_name.replace('.vtt', f".{sub['lang']}.vtt")

            if program_type == 'movie' or len(self.subtitle_language) == 1:
                lang_folder_path = os.path.join(
                    folder_path, f"tmp_{filename.replace('.vtt', '.srt')}")
            else:
                lang_folder_path = os.path.join(
                    os.path.join(folder_path, sub['lang']), f"tmp_{filename.replace('.vtt', '.srt')}")

            os.makedirs(lang_folder_path, exist_ok=True)

            languages.add(lang_folder_path)

            for url in sub['urls']:
                subtitle = dict()
                subtitle['name'] = filename
                subtitle['path'] = lang_folder_path
                subtitle['url'] = url
                subtitle['segment'] = True
                subtitles.append(subtitle)

        self.download_subtitle(subtitles, languages)

    def download_subtitle(self, subtitles, languages):
        if subtitles and languages:
            download_files(subtitles)
            for lang_path in sorted(languages):
                if 'tmp' in lang_path:
                    merge_subtitle_fragments(
                        folder_path=lang_path, filename=os.path.basename(lang_path.replace('tmp_', '')),
                        subtitle_format=self.subtitle_format)


    def get_audio(self, audio_list, folder_path, audio_name):

        for audio in audio_list:

            if audio['lang'] in ['en', 'de']:
                filename = audio_name.replace(
                    '.vtt', f".{audio['lang']}{audio['extension']}")

                self.logger.info("\nDownload: %s\n---------------------------------------------------------------",
                                 filename)
                download_audio(audio['url'], os.path.join(
                    folder_path, filename))


if __name__ == "__main__":

    print(DisneyPlus().series_subtitle())


