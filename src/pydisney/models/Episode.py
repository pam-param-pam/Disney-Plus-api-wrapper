from typing import Optional

from ..Auth import Auth
from ..models.Downloable import MediaTrackSelector
from ..utils.parser import safe_get


class Episode:
    def __init__(self, data):
        self.artwork: Optional[dict] = None
        self.durationMs: Optional[int] = None
        self.brief_description: Optional[str] = None
        self.medium_description: Optional[str] = None
        self.full_description: Optional[str] = None
        self.episodeNumber: Optional[int] = None
        self.episodeTitle: Optional[str] = None
        self.fullEpisodeTitle: Optional[str] = None
        self.rating: Optional[dict] = None
        self.id: Optional[str] = None
        self.resourceId: Optional[str] = None

        self._parse_data(data)

    def _parse_data(self, data) -> None:
        self.id = safe_get(data, ["id"])
        self.resourceId = safe_get(data, ["actions", 0, "resourceId"])
        self.artwork = safe_get(data, ["visuals", "artwork"])
        self.durationMs = safe_get(data, ["visuals", "durationMs"])
        self.brief_description = safe_get(data, ["visuals", "description", "brief"])
        self.medium_description = safe_get(data, ["visuals", "description", "medium"])
        self.full_description = safe_get(data, ["visuals", "description", "full"])

        self.episodeNumber = safe_get(data, ["visuals", "episodeNumber"])
        self.episodeTitle = safe_get(data, ["visuals", "episodeTitle"])
        self.fullEpisodeTitle = safe_get(data, ["visuals", "fullEpisodeTitle"])

        self.rating = safe_get(data, ["visuals", "metastringParts", "ratingInfo", "rating", "text"])

    def __str__(self):
        return f"[Title={self.fullEpisodeTitle}, Episode={self.episodeNumber}]"

    def _get_m3u8_url(self):
        playback_link = "https://disney.playback.edge.bamgrid.com/v7/playback/ctr-regular"
        data = {"playback": {"attributes": {}}, "playbackId": self.resourceId}

        headers = {
            "x-bamsdk-client-id": "disney-svod-9zmsiwec",
            "x-bamsdk-platform": "javascript/windows/chrome",
            "x-bamsdk-version": "32.6",
            "x-dss-edge-accept": "vnd.dss.edge+json; version=2",
            "x-dss-feature-filtering": "true",
            "x-application-version": "1.1.2"
        }

        res = Auth.make_request("POST", playback_link, data=data, headers=headers)
        return res['stream']['sources'][0]['complete']["url"]

    def get_tracks(self) -> MediaTrackSelector:
        url = self._get_m3u8_url()
        return MediaTrackSelector(self.fullEpisodeTitle, url)

    def __repr__(self):
        return self.fullEpisodeTitle
