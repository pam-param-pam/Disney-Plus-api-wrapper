from typing import Optional

from src.pydisney.utils.parser import safe_get


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

        self._parse_data(data)

    def _parse_data(self, data) -> None:
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

    def __repr__(self):
        return self.fullEpisodeTitle
