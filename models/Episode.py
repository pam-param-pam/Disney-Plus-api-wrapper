class Episode:
    def __init__(self, id, number: int, title, videoId):
        self.id = id
        self.number = number
        self.title = title
        self.videoId = videoId
        self.internalTitle = None
        self.mediaId = None
        self.length = None
        self.rating = None
        self.originalLanguage = None
        self.format = None
        self.contentId = None

        self.audioTracks = None
        self.captions = None

    def __str__(self):
        return f"[Title={self.title}, Id={self.id}, Number={self.number}]"

    def __repr__(self):
        return self.title

    def download(self):
        pass