import os
import re
import shutil
from pathlib import Path

import pysubs2

from ..Auth import Auth
from ..Config import APIConfig
from ..models.Downloadable import Downloadable
from ..utils.helper import rename_filename


class Subtitle(Downloadable):

    def __init__(self, language, name, media_id, track_type):
        super().__init__(media_id)
        self.language = language
        self.name = name
        self.track_type = track_type

    def __str__(self):
        return f"Subtitle=[{self.name}, {self.language}]"

    def __repr__(self):
        return self.name

    def is_subtitle(self, file_path, file_format=''):
        extension = Path(file_path).suffix.lower()
        if os.path.isfile(file_path) and Path(file_path).stat().st_size > 0 and extension == ".srt":
            if file_format and file_format != extension:
                return False
            return True
        return False

    def ms_to_timestamp(self, ms: int) -> str:
        max_representable_time = 359999999
        ms = max(ms, 0)
        ms = min(ms, max_representable_time)
        return "%02d:%02d:%02d,%03d" % (pysubs2.time.ms_to_times(ms))

    def convert_list_to_subtitle(self, subs):
        text = ''
        for index, sub in enumerate(subs):
            text = text + str(index + 1) + '\n'
            text = text + self.ms_to_timestamp(sub.start) + ' --> ' + self.ms_to_timestamp(sub.end) + '\n'
            text = text + sub.text.replace('\\n', '\n').replace('\\N', '\n').strip()
            text += '\n\n'

        return pysubs2.ssafile.SSAFile.from_string(text)

    def merge_same_subtitle(self, subs):
        for i, sub in enumerate(subs):
            if i > 0 and sub.text == subs[i - 1].text and sub.start - subs[i - 1].end <= 20:
                subs[i - 1].end = sub.end
                subs.pop(i)
            elif sub.text == '':
                subs.pop(i)
        return subs

    def add_comment(self, subs):
        for sub in subs:
            sub.text = '{\\an8}' + sub.text.strip()
        return subs

    def clean_subs(self, subs):
        for sub in subs:
            text = sub.text
            text = re.sub(r"&rlm;", "", text)
            text = re.sub(r"&lrm;", "", text)
            text = re.sub(r"&amp;", "&", text)
            sub.text = text.strip()
        return subs

    def format_subtitle(self, subs):
        delete_list = []
        for i, sub in enumerate(subs):
            sub.text = re.sub(r'\u200b', '', sub.text)
            sub.text = re.sub(r'\u200e', '', sub.text)
            sub.text = re.sub(r'\u202a', '', sub.text)
            sub.text = re.sub(r'\ufeff', '', sub.text)
            sub.text = re.sub(r'\xa0', ' ', sub.text)

            if sub.text == "":
                delete_list.append(i)

        for i in reversed(delete_list):
            del subs[i]
        return subs

    def _download_subtitle(self, urls, folder_path, name):
        cnt = 0

        for url in urls:
            res = Auth.make_stream_request(url)
            with open(os.path.join(folder_path, f"{str(cnt)}.srt"), 'wb') as file:
                for data in res.iter_content(chunk_size=1024):
                    file.write(data)
            cnt += 1

        self._merge_subtitles(folder_path, name)

    def _merge_subtitles(self, folder_path, name):
        subtitles = []
        for segment in sorted(os.listdir(folder_path)):
            file_path = os.path.join(folder_path, segment)
            if self.is_subtitle(file_path):
                subs = pysubs2.load(file_path)
                subs = self.clean_subs(subs)
                if 'comment' in file_path:
                    self.add_comment(subs)
                subtitles += subs
        subs = self.convert_list_to_subtitle(subtitles)
        subs = self.merge_same_subtitle(subs)
        subs.sort()
        subs = self.format_subtitle(subs)

        subs.save(os.path.join(APIConfig.default_path, name + ".srt"))
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)

    def download(self, name=None):
        if not name:
            name = self.media_id
        name = rename_filename(name)
        m3u8_url = self._get_m3u8_url(self.media_id)

        subtitle, _ = self._parse_m3u(m3u8_url, self.name, "min")

        folder_path = os.path.join(APIConfig.default_path, "tmp")
        os.makedirs(folder_path, exist_ok=True)

        self._download_subtitle(subtitle['urls'], folder_path, name)
