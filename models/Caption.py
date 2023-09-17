import os
import shutil
from pathlib import Path

import pysubs2

from Config import APIConfig
from models.Downloadable import Downloadable
from utils.io import download_files, rename_filename
from utils.subtitle import merge_subtitle_fragments, is_subtitle, clean_subs, add_comment, convert_list_to_subtitle, \
    merge_same_subtitle, format_subtitle


class Caption(Downloadable):

    def __init__(self, language, name, mediaId, trackType):
        super().__init__(mediaId)
        self.language = language
        self.name = name
        self.trackType = trackType

    def __str__(self):
        return f"[{self.name}, {self.language}]"

    def __repr__(self):
        return self.language

    def get_subtitles(self, subtitle, name):
        urls = []
        folder_path = os.path.join(self.default_path, "tmp")
        os.makedirs(folder_path, exist_ok=True)

        for url in subtitle['urls']:

            urls.append(url)

        self.download_subtitle(urls, folder_path, name)

    def download_subtitle(self, urls, folder_path, name):
        x = 0
        headers = {
            'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Safari/537.36"}
        for url in urls:
            res = APIConfig.session.get(url, headers=headers, stream=True, timeout=10)
            with open(os.path.join(folder_path, f"{str(x)}.srt"), 'wb') as file:
                for data in res.iter_content(chunk_size=1024):
                    file.write(data)
            x += 1

        self.merge_subtitles(folder_path, name)

    def merge_subtitles(self, folder_path, name):

        subtitles = []
        for segment in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, segment)
            if is_subtitle(file_path):
                subs = pysubs2.load(file_path)
                subs = clean_subs(subs)
                if 'comment' in file_path:
                    add_comment(subs)
                subtitles += subs
        subs = convert_list_to_subtitle(subtitles)
        subs = merge_same_subtitle(subs)
        subs.sort()
        subs = format_subtitle(subs)

        subs.save(os.path.join(self.default_path, name + ".srt"))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    def download(self, name=None):
        if not name:
            name = self.mediaId

        m3u8_url = self.get_m3u8_url(self.mediaId)

        subtitle, audio = self.parse_m3u(m3u8_url, self.language)

        self.get_subtitles(subtitle, name)
