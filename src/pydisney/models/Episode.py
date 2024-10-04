class Episode:
    def __init__(self, content_id: str, number: int, title: str, video_id: str):
        self.content_id = content_id
        self.number = number
        self.title = title
        self.video_id = video_id

        self.season_number = None
        self.internal_title = None
        self.media_id = None
        self.length = None
        self.rating = None
        self.original_language = None
        self.format = None

        self.audio_tracks = None
        self.subtitles = None

        self.brief_description = None
        self.medium_description = None
        self.full_description = None

    def __str__(self):
        return f"[Title={self.title}, Episode={self.number}, Season={self.season_number}]"

    def __repr__(self):
        return self.title
