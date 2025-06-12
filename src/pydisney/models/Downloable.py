import os
from collections import defaultdict
from dataclasses import dataclass
from typing import Optional, List
from urllib.parse import urljoin

import m3u8
import requests

from ..Config import APIConfig
from ..utils.helper import rename_filename


@dataclass
class Subtitle:
    title: str
    language: str
    uri: str
    name: str = ""
    group_id: str = ""
    forced: str = None

    def download(self, name=None):
        if not name:
            name = self.title + " - " + self.language + ".vtt"
        name = rename_filename(name)

        output_path = os.path.join(APIConfig.default_path, name)

        response = requests.get(self.uri)
        response.raise_for_status()

        lines = response.text.splitlines()
        vtt_segments = [
            urljoin(self.uri, line.strip())
            for line in lines
            if line and not line.startswith("#")
        ]

        with open(output_path, "wb") as outfile:
            for idx, seg_url in enumerate(vtt_segments):
                seg_resp = requests.get(seg_url)
                seg_resp.raise_for_status()
                content = seg_resp.content

                if idx != 0:
                    content = b"\n".join(content.splitlines()[1:])
                outfile.write(content + b"\n")

        return output_path

    def __str__(self):
        return f"Subtitle[language='{self.language}', name='{self.name}', forced={self.forced}, title='{self.title}']"

    def __repr__(self):
        return self.__str__()


@dataclass
class Audio:
    title: str
    language: str
    uri: str
    name: str = ""
    group_id: str = ""
    quality: str = ""
    codec: str = ""
    channels: str = ""

    def download(self, name=None):
        if not name:
            ext = self.codec
            if self.codec == "eac":
                ext = "ac3"
            name = self.title + " - " + self.language + "." + ext

        name = rename_filename(name)

        output_path = os.path.join(APIConfig.default_path, name)

        os.system(
            f'ffmpeg -protocol_whitelist file,http,https,tcp,tls,crypto -i "{self.uri}" -c copy "{output_path}" -preset ultrafast -loglevel warning -hide_banner -stats')

    def __str__(self):
        return f"Audio[language='{self.language}', name='{self.name}', title='{self.title}', quality={self.quality}, codec={self.codec}, channels={self.channels}]"

    def __repr__(self):
        return self.__str__()


class AudioTrackGroup:
    def __init__(self, tracks: List['Audio']):
        self._tracks = tracks

    def all(self):
        return self._tracks

    def filter_by_quality(self, quality: str):
        return AudioTrackGroup([t for t in self._tracks if t.quality == quality])

    def filter_by_codec(self, codec: str):
        return AudioTrackGroup([t for t in self._tracks if (t.codec or "").lower() == codec.lower()])

    def get_best_quality(self, preferred_codecs: Optional[List[str]] = None) -> Optional['Audio']:
        def parse_quality(q: str) -> int:
            try:
                return int(q.replace("k", "")) * 1000
            except (AttributeError, ValueError):
                return 0

        def codec_rank(codec: str):
            if preferred_codecs:
                try:
                    return preferred_codecs.index(codec.lower())
                except ValueError:
                    return len(preferred_codecs)
            return 0

        return max(
            self._tracks,
            key=lambda a: (
                parse_quality(a.quality),
                int(a.channels or 0),
                -codec_rank(a.codec)
            ),
            default=None
        )

    def first(self) -> Optional['Audio']:
        return self._tracks[0] if self._tracks else None

    def __str__(self):
        return f"AudioTrackGroup[length={len(self._tracks)}]"

    def __repr__(self):
        return self.__str__()

class SubtitleTrackGroup:
    def __init__(self, tracks: List['Subtitle']):
        self._tracks = tracks

    def all(self):
        return self._tracks

    def get_forced(self):
        return SubtitleTrackGroup([t for t in self._tracks if t.forced])

    def get_unforced(self):
        return SubtitleTrackGroup([t for t in self._tracks if not t.forced])

    def first(self) -> Optional['Subtitle']:
        return self._tracks[0] if self._tracks else None

    def __str__(self):
        return f"SubtitleTrackGroup[length={len(self._tracks)}]"

    def __repr__(self):
        return self.__str__()

class MediaTrackSelector:
    def __init__(self, title, m3u8_content):
        self.title = title
        self.subs, self.audios = self._parse_m3u8_from_url(m3u8_content)

    def _parse_m3u8_from_url(self, url):
        m3u8_obj = m3u8.load(url)
        subs = defaultdict(list)
        audios = defaultdict(list)

        for media in m3u8_obj.media:
            if not media.language:
                continue

            full_uri = urljoin(url, media.uri)
            lang_key = media.language.lower()
            if media.type == "SUBTITLES":
                subs[lang_key].append(
                    Subtitle(
                        title=self.title,
                        language=lang_key,
                        uri=full_uri,
                        name=media.name,
                        group_id=media.group_id,
                        forced=media.forced == "YES"
                    )
                )
            elif media.type == "AUDIO":
                group_id = media.group_id or ""
                parts = group_id.split("-")
                codec = parts[0] if len(parts) > 0 else ""
                quality = parts[1] if len(parts) > 1 else ""

                audios[lang_key].append(
                    Audio(
                        title=self.title,
                        language=lang_key,
                        uri=full_uri,
                        name=media.name or "",
                        group_id=group_id,
                        quality=quality,
                        codec=codec,
                        channels=media.channels
                    )
                )
        return subs, audios

    def get_audios(self, language="en") -> AudioTrackGroup:
        return AudioTrackGroup(self.audios.get(language.lower(), []))

    def get_subtitles(self, language="en") -> SubtitleTrackGroup:
        return SubtitleTrackGroup(self.subs.get(language.lower(), []))

    @property
    def all_audios(self):
        return list(self.audios.values())

    @property
    def all_subtitles(self):
        return list(self.subs.values())

    def available_languages(self):
        return {
            "subtitles": list(self.subs.keys()),
            "audio": list(self.audios.keys())
        }

    def __str__(self):
        return f"MediaTrackSelector[audio={len(self.audios)}, subtitle={len(self.subs)}]"
